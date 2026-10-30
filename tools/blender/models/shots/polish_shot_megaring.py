"""The Rear Mega Pulse's shots (shots sheet sprites 208, 209, 256 and 257, all 1x1: 12 x 14 cells), modelled
(2026-10-30, the third round of the energy shots' models; until then each was drawn as its sprite with volume and the
automatic glow). Built with polish_shot_sonic.py's Wave (a band between two edges, round on top, on its bands' borders)
and polish_shot_fireball.py's kit (Loft for the flame tongues, dome_core for the spark); the nearest model before,
polish_launched_flames.py's pulse_ring (SAVARA's rings), cuts its faces along the bands (band_split): not used.

Who fires them: the Rear Mega Pulse (rear port 22, shop 1:12, 900), a volley every 2-6 frames:
  power  1: 256 (left, 9 pixels a frame)          power  7: 256 257 (10), 209 (down, 9), 208 (up, 9)
  power  2-3: 256 257 (left, right)               power  8-9: 256 257 (12), 209 209 (down, 6 left and right)
  power  4: 256 257, 209 (down)                   power 10: 209, 256 257 twice (7 above and below)
  power  5: 256 257 twice (14 apart)              power 11: 209, 256 257 twice, 208 (up, 13)
  power  6: 256 257, 209
Nothing else draws them (the second player's turret of rear port 22 takes the pulse's twin bolts, linkMult2Gr).

As the sprites draw them (ramp 7, the fire: 0x70 black-red .. 0x79 orange .. 0x7c yellow): a ring of fire 12 pixels
across and 8 deep (208: rows 0-7), wider than deep across its flight, its band 2-3 pixels wide: its crest brightest at
its sides (0x79), orange-red at its front and back (0x76-0x78), its outer edge dark red (0x71-0x74), its inner edge
0x73; inside it a dark eye (0x70) 6 x 4 with a spark in it (0x7c, 0x78); three flame tongues trailing behind it (0x75
to 0x71, 4 pixels long). 208 flies up the screen (the ring at the top, the tongues hanging down), 209 down (208 upside
down), 256 left and 257 right (lying on its side, the tongues trailing to the right or left).

The model (shot_megaring, authored as 208 draws it, turned onto 209, 256 and 257 by yaw= with at=): the band a Wave
closed round the ring (outer edge an ellipse 12 x 8.6, inner edge the eye's ellipse 6 x 4), round on top with its crest
in the band's middle, its heat brightest along the crest at the sides and falling to its edges, its bands' borders
rings of the mesh; the eye a dark membrane (0x70, no glow) a little above the ground inside it, the band's inner slope
over its rim; the spark a small dome of yellow on the eye, a little to the front of its middle; the three tongues
Lofts (their roots inside the band's back). 7 materials.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); built on z = 0.

models.cfg: see the block's comment; --check prints each line's silhouette and the at= that lays the turned ring on
its sprite.

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_megaring.py -- [--outdir <dir>] (default
     assets/models/shots) [--check <sheets dir>] (silhouettes against <dir>/shots.png) [--preview <prefix>]
"""
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_fireball as kit  # noqa: E402
import polish_shot_sonic as sonic  # noqa: E402
from polish_shot_fireball import k, mk, triangulate, view  # noqa: E402

# The ring (as 208 draws it): the outer edge's middle and half-axes, the eye's (the inner edge), the samples round it;
# the crest's height round it (|u|: 0 the front, 0.5 the sides, 1 the back), where it lies across the band; the heat
# along the crest (|u|) and how much it falls to the outer and the inner edge.
RING = dict(outer=((0.0, 2.75), 6.0, 4.3), inner=((0.0, 3.0), 3.05, 2.05), samples=40,
            height=((0.0, 1.05), (0.25, 1.3), (0.5, 1.45), (0.75, 1.3), (1.0, 1.15)), crest=0.45, back=0.7,
            along=((0.0, 7.0), (0.2, 7.8), (0.4, 8.9), (0.5, 9.2), (0.62, 8.9), (0.8, 7.9), (1.0, 7.4)),
            front=0.68, back_drop=0.6, peak=0.45)
BANDS = [(-99.0, 0x72, 0.2), (3.2, 0x74, 0.26), (5.0, 0x76, 0.33), (6.8, 0x77, 0.38), (8.2, 0x79, 0.46)]
# The eye: its height over the ground and how far its rim reaches under the band (pixels); dark, no glow.
EYE = (0.24, 0.35, 0x70)
# The spark: its middle, half-axes, lift over the eye, bands from its middle out.
SPARK = ((0.0, 3.45), 0.95, 0.8, 0.6, ((0.0, 0x7c, 0.56), (0.5, 0x79, 0.46)))  # (its rim the band's 0x79)
# The tongues: x, the y of their root (inside the band's back) and tip, half-width; the heat along them.
TONGUES = [(-3.5, 0.6, -5.0, 0.5), (0.0, 0.2, -5.1, 0.62), (3.5, 0.6, -5.0, 0.5)]
TONGUE_ALONG = ((0.0, 5.8), (0.3, 5.0), (0.65, 3.6), (1.0, 1.4))
TONGUE_ACROSS = ((0.0, 1.0), (1.0, 1.2))
# The lines: (sprite, yaw, at dx, at dy) (at= fitted with --check).
LINES = [(208, 0.0, 0.0, 0.0), (209, 180.0, 0.0, 0.0), (256, 270.0, 0.0, 0.0), (257, 90.0, 0.0, 0.0)]
HOT = (0.0, 3.0)  # (the ring's middle: where the glow goes)


def ellipse(centre, a, b, theta):
    """A point of the ellipse at the angle theta from its top, clockwise."""
    return centre[0] + a * math.sin(theta), centre[1] + b * math.cos(theta)


def build_ring(name):
    mats = kit.materials("megaring_fire", BANDS)
    spec = RING
    n = spec["samples"]
    thetas = [2 * math.pi * j / n for j in range(n)]
    outer = [ellipse(spec["outer"][0], spec["outer"][1], spec["outer"][2], t) for t in thetas]
    inner = [ellipse(spec["inner"][0], spec["inner"][1], spec["inner"][2], t) for t in thetas]
    us = [((t + math.pi) % (2 * math.pi) - math.pi) / math.pi for t in thetas]  # (-1 .. 1, 0 the front)
    band = sonic.Wave(outer, inner, us, sonic.height_curve(spec["height"]),
                      sonic.heat_field(spec["along"], spec["front"], spec["back_drop"], spec["peak"], 1.2), BANDS,
                      crest=spec["crest"], back=spec["back"], closed=True, waves=(4.0, 0.02, 1.9), gap=0.3)
    parts = [band.build(name + "_band", mats)]
    # The eye: a flat ellipse a little above the ground, its rim under the band's inner slope.
    height, reach, index = EYE
    (cx, cy), a, b = spec["inner"]
    eye_mat = kit.lit("megaring_eye_%02x" % index, index, 0.0, roughness=0.6)
    count = 28
    verts = [(cx, cy, height)] + [(cx + (a + reach) * math.sin(2 * math.pi * j / count),
                                   cy + (b + reach) * math.cos(2 * math.pi * j / count), height) for j in range(count)]
    faces = [(0, 1 + (j + 1) % count, 1 + j) for j in range(count)]
    eye = k.mesh_object(name + "_eye", verts, faces, eye_mat)
    k.recalc_normals(eye)
    # (a flat disc: make sure it faces up)
    if eye.data.polygons[0].normal.z < 0:
        eye.data.flip_normals()
    parts.append(eye)
    # The spark on the eye.
    (sx, sy), rx, ry, lift, sbands = SPARK
    smats = [kit.materials("megaring_spark", sbands[:1], kit.CORE_ROUGHNESS)[0], mats[-1]]
    parts.append(kit.dome_core(name + "_spark", (sx, sy), rx, ry, lift, lambda x, y: height, sbands, smats,
                               segments=12, tongues=(3, 0.0, 1.0)))
    # The tongues trailing behind.
    for i, (x, root, tip, w) in enumerate(TONGUES):
        loft = kit.Loft(x, root, tip, sonic.streak_width(w), kit.loft_heat(TONGUE_ALONG, TONGUE_ACROSS), BANDS,
                        depth=0.62, segments=5, tongues=(2.0, 0.02, 1.2), gap=0.25, width_gap=0.5,
                        head_fractions=(0.2,), tail_fractions=(0.5,))
        parts.append(loft.build(name + "_tongue%d" % i, mats))
    return parts


def build():
    options = k.args()
    outdir = options.get("outdir", kit.OUTDIR)
    name = "shot_megaring"
    k.reset()
    parts = triangulate(build_ring(name))
    bpy.context.view_layer.update()
    print("== %s (shots %s): a ring of fire with a dark eye" % (name, " ".join(str(l[0]) for l in LINES)))
    if "check" in options:
        sonic.check_one(name, parts, options["check"], [("shots",) + l for l in LINES], HOT)
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(name, parts, os.path.join(outdir, name + ".glb"))
    if "preview" in options:
        view(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
