"""The enemies' minor shots (shots sheet sprites 162, 304, 7, 45 and 260, all 1x1: 12 x 14 cells), modelled
(2026-10-29, round 2 of the energy shots' models; until then each was drawn as its sprite with volume, flat, from the
4x sheets, with the automatic glow). None is animated (their weapons' weapani 0) and none picks its sprite by heading:
each is drawn as the sprite is, yaw 0.

- 162 (enemy weapon 132: SOH JIN's and MISTAKES' craft, falling down the screen at 6; EYESPY's once a fire override
  event gives them a frequency): two small beads of fire one above the other (columns 4-7 of rows 2-5 and 7-10, their
  middles on the cell's middle column, 3 pixels above and 2 below its centre), each 4 pixels across, yellow-orange
  (0x7a, 0x7b) round a pale yellow and white heart (0x7d-0x7f). Model shot_eminor_162: two of polish_shot_pellet.py's
  beads, 4 pixels across, their hearts standing out of them.
- 304 (enemy weapons 142 and 144: a spray of three or five thrown up and falling back (acceleration 1) from DELI's,
  New Deli's, BONUS', TORM's, SOH JIN's, GRYPHON's, BOTANY's and SAVARA's ground guns and the asteroid levels' rocks;
  the SandStorm special's sparks): a tiny spark, a diamond 5 pixels across (rows 5-9, columns 4-8, its middle that of
  pixel (6, 7)): dark red points (0x73) round orange (0x79) and a yellow middle (0x7d). Model shot_eminor_304: a
  four-pointed star of fire (its sides a little hollow), ridged along its arms, a yellow heart in its middle.
- 7 (enemy weapon 46: DELI's and New Deli's wall guns, falling down the screen at 10) and 45 (weapon 55, the same
  guns' other side): a fireball drawn on its side, flying right (7) or left (45: 7's mirror image): 11 pixels long
  and 8 high (rows 2-9), its head round and hottest 3 pixels from its front (0x7d, 0x7b round it at column 8 of 7), a
  dark red rim in front of it (0x74, 0x77), the fire cooling slowly back along its tail to near black (0x70) and to
  dark red at its upper and lower edges. Models shot_eminor_7 and shot_eminor_45 (its mirror image: the beads lean
  towards the camera, so 45 is built mirrored, not turned): a teardrop of fire round its head, its bands by a heat
  that falls fast to the front, slower to the sides and slowest back along the tail, a heart of yellow plasma standing
  out of the head, drawn out backwards as the sprite's hot wedge is.
- 260 (enemy weapon 69: BOTANY B's pods, two side by side 12 pixels apart, falling at 3): a red capsule 7 pixels wide
  and 14 long (columns 2-8, all 14 rows; its middle half a pixel left of the cell's), its corners cut, a dark rim
  (0x71) round red (0x75), orange (0x79) and a hot spine down its middle column (0x7a-0x7e, hottest in the middle).
  Model shot_eminor_260: a capsule of fire (as high all along its middle, rounded at its ends), its bands by that heat
  in stripes along it, a long thin heart of plasma standing out of it along the spine.

Every model is polish_shot_pellet.py's bead (class Bead: a dome of fire round on top and flat underneath, built on
rings round its middle that are the bands' borders, so no face is cut; its height from the distance to its outline;
leant towards the camera so that the camera sees the rings where the sprite lays them out) with its outline and heat
for the sprite. Palette materials of ramp 7, every band glowing in its own colour, more the hotter (0.2-0.5 the fire,
0.52-0.6 the hearts: CONVENTIONS section 4); the flat undersides take the rim's material. 162: 464 triangles, 5
materials; 304: 304, 5; 7 and 45: 660, 7; 260: 664, 6. Each line's glow= is a small halo in the fire's orange (0x79;
162's in its yellow-orange, 0x7b) on the shot's hot part.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r, its top edge y = 7 - r);
the shots stand on z = 0 (the game centres shot models in height on the player's layer).

models.cfg (the shots section):
    model shot_eminor_162 shots/shot_eminor_162.glb   (and _304, _7, _45, _260)
    shot shots 162 shot_eminor_162 glow=11:0.5:123:0:-0.5     # two small beads
    shot shots 304 shot_eminor_304 glow=8:0.5:121:0.5:0.5     # a spark
    shot shots 7   shot_eminor_7   glow=12:0.55:121:2.5:-1    # a fireball flying right
    shot shots 45  shot_eminor_45  glow=12:0.55:121:-2.5:-1   # flying left
    shot shots 260 shot_eminor_260 glow=13:0.5:121:-0.5:0     # a red capsule

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_eminor.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] [--preview <prefix>]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from polish_shot_pellet import Bead, Outline, bead, materials, run  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_flame_drop import monotone  # noqa: E402
import polish_machine_kit as mk  # noqa: E402

FIRE_ROUGHNESS, HEART_ROUGHNESS = 0.5, 0.4


def polygon_radius(points, centre):
    """The outline through points (a closed polygon round centre, smoothed: Chaikin) as its radius at each angle round
    centre (where the ray from centre leaves it)."""
    smooth = mk.chaikin(points, 2, closed=True)
    cx, cy = centre

    def radius(angle):
        dx, dy = math.cos(angle), math.sin(angle)
        best = 0.0
        for (ax, ay), (bx, by) in zip(smooth, smooth[1:] + smooth[:1]):
            ex, ey = bx - ax, by - ay
            den = dx * ey - dy * ex
            if abs(den) < 1e-12:
                continue
            t = ((ax - cx) * ey - (ay - cy) * ex) / den  # along the ray
            s = ((ax - cx) * dy - (ay - cy) * dx) / den  # along the edge
            if t > 0 and -1e-9 <= s <= 1 + 1e-9:
                best = max(best, t)
        return best
    return radius


def directional(front, side, back):
    """A heat (u, angle) -> shade from three curves out from the middle ((u, shade) points): along +x (front), along y
    (side) and along -x (back), blended by the angle."""
    f, s, b = (monotone([p[0] for p in c], [p[1] for p in c]) for c in (front, side, back))

    def heat(u, angle):
        c = math.cos(angle)
        wf, wb = max(c, 0.0) ** 2, max(-c, 0.0) ** 2
        return wf * f(u) + wb * b(u) + (1.0 - wf - wb) * s(u)
    return heat


# --- 162: two small beads ---------------------------------------------------------------------------------------------
BEAD_162 = dict(radius=2.0, height=1.6, middles=((0.0, 3.0), (0.0, -2.0)),
                heat=((0.0, 14.6), (0.35, 14.0), (0.79, 10.6), (1.0, 9.6)),
                bands=[(-99.0, 0x79, 0.44), (11.2, 0x7b, 0.5), (13.0, 0x7c, 0.54)],
                heart=(0.5, 0.3, ((0.0, 0x7e, 0.6), (0.55, 0x7d, 0.58))))


def model_162(name):
    spec = BEAD_162
    fire = materials("eminor_fire", spec["bands"], FIRE_ROUGHNESS)
    hearts = materials("eminor_heart", spec["heart"][2], HEART_ROUGHNESS)
    parts = []
    for i, (x, y) in enumerate(spec["middles"]):
        b = Bead(x, y, spec["radius"], spec["height"], spec["heat"], spec["bands"],
                 (spec["heart"][0], spec["heart"][0], spec["heart"][1], spec["heart"][2]),
                 flames=(4, 0.04, 1.9, 0.05), segments=14, heart_segments=8, head_rings=(0.5,),
                 rim_rings=(0.93, 1.0), heart_rings=(0.4, 0.75, 1.0))
        parts += bead(f"{name}_{i}", b, fire, hearts)
    return parts


# --- 304: the spark ---------------------------------------------------------------------------------------------------
SPARK = dict(middle=(0.5, -0.5), tip=2.6, hollow=0.85, height=1.5,
             heat=((0.0, 13.0), (0.4, 9.0), (0.8, 3.2), (1.0, 2.0)),
             bands=[(-99.0, 0x73, 0.26), (5.0, 0x76, 0.34), (7.6, 0x79, 0.46)],
             heart=(0.38, 0.3, ((0.0, 0x7d, 0.58), (0.55, 0x7b, 0.54))))


def model_304(name):
    spec = SPARK
    tip, p = spec["tip"], spec["hollow"]

    def radius(angle):
        return tip / (abs(math.cos(angle)) ** p + abs(math.sin(angle)) ** p) ** (1.0 / p)
    b = Bead(*spec["middle"], radius, spec["height"], spec["heat"], spec["bands"],
             (spec["heart"][0], spec["heart"][0], spec["heart"][1], spec["heart"][2]),
             flames=(4, 0.0, 0.0, 0.0), segments=24, heart_segments=8, head_rings=(0.5,), rim_rings=(0.93, 1.0),
             heart_rings=(0.4, 0.75, 1.0))
    return bead(name, b, materials("eminor_fire", b.bands, FIRE_ROUGHNESS),
                materials("eminor_heart", b.heart[3], HEART_ROUGHNESS))


# --- 7 and 45: the fireball on its side -------------------------------------------------------------------------------
# 7's outline (the sprite's rows smoothed; its middle row y = 1), its hottest point (column 8 of rows 5-6) and its heat
# out from there: to the front (+x, 3.5 pixels to the rim), up and down (4) and back along the tail (7.9).
FIREBALL = dict(
    outline=[(6.0, 1.0), (6.0, 2.6), (5.3, 3.8), (4.2, 4.7), (2.5, 5.0), (0.0, 5.0), (-2.6, 4.8), (-3.6, 3.6),
             (-4.6, 2.5), (-5.4, 1.0), (-4.6, -0.5), (-3.6, -1.6), (-2.6, -2.8), (0.0, -3.0), (2.5, -3.0),
             (4.2, -2.7), (5.3, -1.8), (6.0, -0.6)],
    hot=(2.5, 1.0), height=3.0,
    front=((0.0, 13.2), (0.29, 10.2), (0.57, 7.0), (0.86, 4.0), (1.0, 3.0)),
    side=((0.0, 13.2), (0.375, 11.0), (0.625, 8.0), (0.875, 4.0), (1.0, 3.0)),
    back=((0.0, 13.2), (0.127, 11.0), (0.25, 10.0), (0.38, 8.0), (0.51, 4.2), (0.63, 2.0), (0.76, 1.0), (1.0, 0.0)),
    bands=[(-99.0, 0x72, 0.22), (2.5, 0x74, 0.27), (5.0, 0x77, 0.37), (7.5, 0x79, 0.45), (9.6, 0x7b, 0.5)],
    heart=(0.3, 0.3, 0.4, ((0.0, 0x7d, 0.58), (0.55, 0x7c, 0.56))))


def model_fireball(name, mirrored):
    spec = FIREBALL
    sign = -1.0 if mirrored else 1.0
    outline = [(sign * x, y) for x, y in spec["outline"]]
    hot = (sign * spec["hot"][0], spec["hot"][1])
    radius = polygon_radius(outline if not mirrored else outline[::-1], hot)
    heat = directional(spec["front"], spec["side"], spec["back"])
    if mirrored:
        flat = heat
        heat = lambda u, angle: flat(u, math.pi - angle)  # noqa: E731
    sx, sy, lift, bands = spec["heart"]
    b = Bead(*hot, radius, spec["height"], heat, spec["bands"], (sx, sy, lift, bands),
             flames=(5, 0.035, 1.9, 0.08), segments=30, heart_segments=12, heart_rings=(0.35, 0.65, 0.88, 1.0))
    return bead(name, b, materials("eminor_fire", b.bands, FIRE_ROUGHNESS),
                materials("eminor_heart", b.heart[3], HEART_ROUGHNESS))


# --- 260: the capsule -------------------------------------------------------------------------------------------------
# Its outline (the sprite's rows, the corners cut, smoothed), its middle, the spine's heat out along it (|y|) and how
# the heat falls off across it (times the spine's, by |x| from the middle).
CAPSULE = dict(
    outline=[(3.0, -4.6), (3.0, 4.6), (2.6, 5.6), (1.8, 6.5), (0.6, 7.0), (-1.6, 7.0), (-2.8, 6.5), (-3.6, 5.6),
             (-4.0, 4.6), (-4.0, -4.6), (-3.6, -5.6), (-2.8, -6.5), (-1.6, -7.0), (0.6, -7.0), (1.8, -6.5),
             (2.6, -5.6)],
    middle=(-0.5, 0.0), height=2.9,
    spine=((0.0, 13.8), (0.5, 13.5), (1.5, 12.0), (2.5, 11.0), (3.5, 10.0), (4.5, 9.0), (5.5, 7.0), (6.5, 2.5),
           (7.0, 1.0)),
    across=((0.0, 1.0), (1.0, 0.68), (2.0, 0.38), (3.0, 0.1), (3.5, 0.0)),
    bands=[(-99.0, 0x71, 0.2), (2.4, 0x74, 0.27), (5.0, 0x77, 0.37), (7.6, 0x79, 0.45)],
    heart=(0.2, 0.84, 0.35, ((0.0, 0x7d, 0.58), (0.55, 0x7b, 0.52))))


def model_260(name):
    spec = CAPSULE
    cx, cy = spec["middle"]
    radius = polygon_radius(spec["outline"], spec["middle"])
    spine = monotone([p[0] for p in spec["spine"]], [p[1] for p in spec["spine"]])
    across = monotone([p[0] for p in spec["across"]], [p[1] for p in spec["across"]])

    def heat(u, angle):
        r = u * radius(angle)
        return spine(abs(r * math.sin(angle))) * across(abs(r * math.cos(angle)))
    b = Bead(cx, cy, radius, spec["height"], heat, spec["bands"], spec["heart"],
             flames=(6, 0.025, 1.9, 0.06), segments=34, heart_segments=12, heart_rings=(0.35, 0.65, 0.88, 1.0))
    return bead(name, b, materials("eminor_fire", b.bands, FIRE_ROUGHNESS),
                materials("eminor_heart", b.heart[3], HEART_ROUGHNESS))


# name: (sprite, what it is, builder)
MODELS = [
    ("shot_eminor_162", 162, "two small beads one above the other", model_162),
    ("shot_eminor_304", 304, "a spark: a four-pointed star of fire", model_304),
    ("shot_eminor_7", 7, "a fireball on its side, flying right", lambda name: model_fireball(name, False)),
    ("shot_eminor_45", 45, "the fireball flying left (7's mirror image)", lambda name: model_fireball(name, True)),
    ("shot_eminor_260", 260, "a red capsule with a hot spine", model_260),
]


def build_model(name, sprite, builder):
    return triangulate(builder(name))


if __name__ == "__main__":
    run(MODELS, build_model)
