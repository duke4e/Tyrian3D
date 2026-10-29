"""FLEET's small fireball (sheet K sprite 171, 1x1: a 7 x 14 drop in the 12 x 14 cell; enemy 710 of episode 3, the top
layer; one frame, not animated), modelled (2026-10-29; until now it had no model and was drawn as an HD volume).
models.cfg: model fleet_fireball enemies/fleet_fireball.glb, sprite k 171 fleet_fireball yaw=0 glow=9:0.3:122:-0.5:2.5
(the glow: the fire's orange round the core).

What it is: what FLEET's lamp guns (enemy 706, K 278, polish_k_lampgun.py) drop on the player: their launch type is 710,
and the level's event 31 (Enemy Fire Override, which gives every enemy of its link that has a launch type a launch
frequency) sets them going, so from the clock 1672 on they let fall a string of these from their lamps (the top layer's
lamp guns into the top layer, slots 50-74; the sky's into the sky); each falls straight down the screen, fast ((0, 6)
and the scroll), armour 5, worth 10. Launched enemies are made by their launcher (catalog.json lists none of them;
TYR3D_LOG_SPAWNS prints them as "appear: ... enemy 710 sprite 171"). No other enemy shows the sprite; it is no other
sprite's pixels mirrored, turned or in other ramps.

As the sprite draws it (columns 2-8, rows 0-13; its middle column 5, half a pixel left of the cell's): a drop of fire
falling, its round head down the screen and its tail streaming up to a point at row 0, round a blue-white core in the
head (columns 3-7 of rows 7-11, ramp 3: white 0x3f in its middle at row 9, 0x3a-0x3c round it, a darker blue rim
0x34-0x37); the fire (ramp 7) wraps the core, orange at its sides (0x77-0x79 down columns 2 and 8) and hottest under
it (0x7b at row 12: the head leads), the tail dark red at its edges (0x71-0x73), lighter up its middle (0x75, 0x77,
0x78, 0x7a from row 3 down to the core).

The model: the fire's drop lofted along the screen's y (round sections, fuller towards the camera than underneath),
its outline the sprite's rows smoothed (polish_flame_drop's Outline), three tongues of flame raised along the tail's
upper side (ridges that waver a little as they go, fading out into the head and at the tip); painted with the
sprite's heat (its ramp 7 shades smoothed, polish_flame_drop's Heat, the core's place filled in from the fire round
it) in bands of ramp 7's palette indices along smooth borders (polish_orb_red.band_split), cooler where the surface
turns away from the game's camera and down the tongues' sides, hotter along their crests, the underside the dark red
of the rim; every band glows in its own colour, more the hotter (0.18-0.56: the fire gives its own light, so it reads
in FLEET's dark as the sprite does). The core: a ball of blue-white plasma in the head, standing out of the fire's
front so that the camera sees it ringed by the fire as the sprite draws it, painted in bands of ramp 3 by how far it
faces the game's camera (0x3e in its middle, darker blues out to 0x35 at its rim: the sprite's lighter blues washed to
grey under the sun and the bloom) and glowing (0.18-0.44). The game's bloom and models.cfg's glow add on top. About
4 200 triangles; 14 materials.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); the drop's axis lies in
z = 0 (the game centres it in height on its layer).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_K.png), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_flame_drop import Heat, Outline  # noqa: E402
from polish_launched_flames import grid, shades, lit, smoothstep, vertex_normals, check_frames, turn  # noqa: E402

NAME = "fleet_fireball"
SPRITE = 171
TOP = 7.0  # the y of a 1x1 sprite's top edge

K_171 = """
.. .. .. .. .. 71 .. .. .. .. .. ..
.. .. .. .. 71 72 71 .. .. .. .. ..
.. .. .. .. 72 73 72 .. .. .. .. ..
.. .. .. 71 73 75 73 71 .. .. .. ..
.. .. .. 72 74 77 74 72 .. .. .. ..
.. .. .. 74 75 78 75 74 .. .. .. ..
.. .. 71 75 75 7a 75 75 71 .. .. ..
.. .. 73 76 34 39 34 76 73 .. .. ..
.. .. 77 34 3a 3c 3b 34 77 .. .. ..
.. .. 78 35 3c 3f 3b 35 78 .. .. ..
.. .. 79 36 3b 3b 39 36 79 .. .. ..
.. .. 73 79 37 38 37 79 73 .. .. ..
.. .. .. 73 79 7b 79 73 .. .. .. ..
.. .. .. .. 73 75 73 .. .. .. .. ..
"""

# The game's camera: 20 degrees from straight down, from the bottom of the screen (the direction towards it).
VIEW = Vector((0.0, -math.sin(math.radians(20.0)), math.cos(math.radians(20.0))))

# The drop: its outline (the sprite's rows smoothed, closing to a point POINT past its top row and rounding off below
# its bottom one), the half-depths above and below its axis (times the half-width), the rings along it (STEP apart) and
# the points round each.
POINT = 0.55
BOTTOM_ROUND = ((0.3, 0.86), (0.48, 0.55), (0.56, 0.0))
DEPTH = (0.86, 0.72)
STEP = 0.4
SEGMENTS = 28
# The tongues: how many round the drop (ridges, one along the top towards the camera), how far their crests stand out
# (pixels), how they waver (radians round the drop, a wave along y: amplitude, wavelength), where they grow in from the
# head and fade out at the tip (y), and how much hotter their crests are (shades).
TONGUES = 5
TONGUE_LIFT = 0.24
WAVER = (0.22, 3.4)
TONGUE_FROM, TONGUE_TO = (-1.2, 1.6), (4.8, 6.6)
TONGUE_HEAT = 1.6
# The heat: the sprite's shades scaled, the side turning away from the camera cooler (heat times SIDE_COOL[0] +
# SIDE_COOL[1] * smoothstep(SIDE_COOL[2], SIDE_COOL[3], the normal's part towards the camera)).
FIRE_GAIN = 1.3
SIDE_COOL = (0.55, 0.45, -0.35, 0.6)
# The bands: (lowest heat, palette index, emission strength in the palette colour), ramp 7 from the rim's dark red to
# yellow; low glows (the game's bloom and models.cfg's glow add on top).
FIRE_BANDS = [(-99.0, 0x71, 0.18), (2.0, 0x72, 0.22), (3.3, 0x73, 0.26), (4.6, 0x75, 0.3), (6.2, 0x77, 0.36),
              (8.0, 0x79, 0.42), (9.6, 0x7a, 0.47), (10.8, 0x7b, 0.52), (11.8, 0x7c, 0.56)]
# The core: its middle (the sprite's column 5, row 9) and radius, how far it stands out towards the camera (its
# middle's z), and its bands by how far it faces the camera (the lowest part of the view direction, palette index,
# emission strength).
CORE = (-0.5, -2.5)
CORE_R = 2.55
CORE_Z = 1.25
CORE_BANDS = [(-99.0, 0x35, 0.18), (0.45, 0x37, 0.24), (0.62, 0x39, 0.3), (0.78, 0x3b, 0.36), (0.92, 0x3e, 0.44)]


def tongue_ridge(t, y):
    """How far up a tongue's crest a point is (-1 a trough, 1 a crest) at the angle t round the drop (pi / 2 on top),
    with the envelope along y (0 in the head and at the tip)."""
    wave = WAVER[0] * math.sin(2 * math.pi * y / WAVER[1])
    ridge = math.cos(TONGUES * (t - math.pi / 2 - wave))
    grow = float(smoothstep(TONGUE_FROM[0], TONGUE_FROM[1], y))
    fade = float(smoothstep(TONGUE_TO[0], TONGUE_TO[1], y))
    return ridge, grow * (1.0 - fade)


def fire(name):
    rows = grid(K_171)
    outline = Outline([[None if i is None else 0 for i in row] for row in rows], TOP, soften=1, point=POINT,
                      bottom_round=BOTTOM_ROUND)
    heat = Heat(shades(rows, 7), TOP, sigma=(0.6, 0.7))
    count = max(8, int(round((outline.y1 - outline.y0) / STEP)))
    ys = [outline.y0 + (outline.y1 - outline.y0) * (i + 0.5) / count for i in range(count)]
    ys = sorted(set(ys) | {outline.y0 + d for d in (0.05, 0.14)} | {outline.y1 - d for d in (0.05, 0.14)})
    rings, info = [], []
    for y in ys:
        w = max(outline.width(y), 0.02)
        cx = outline.middle(y)
        ring = []
        for j in range(SEGMENTS):
            t = 2 * math.pi * j / SEGMENTS
            c, s = math.cos(t), math.sin(t)
            depth = DEPTH[0] if s >= 0 else DEPTH[1]
            ridge, env = tongue_ridge(t, y)
            on_top = max(0.0, s) ** 0.5  # the tongues on the side the camera sees
            nx, nz = c / w, s / (w * depth)
            nl = math.hypot(nx, nz) or 1.0
            lift = TONGUE_LIFT * env * on_top * ridge
            ring.append(Vector((cx + w * c + lift * nx / nl, y, w * s * depth + lift * nz / nl)))
            info.append(ridge * env * on_top)
        rings.append(ring)
    obj = k.loft(name, rings, None, start_point=(outline.middle(outline.y0), outline.y0, 0.0),
                 end_point=(outline.middle(outline.y1), outline.y1, 0.0))
    info += [0.0, 0.0]  # the end points
    normals = vertex_normals(obj)
    values = []
    for v, n, ridge in zip(obj.data.vertices, normals, info):
        h = heat(v.co.x, v.co.y) * FIRE_GAIN
        facing = n.dot(VIEW)
        h *= SIDE_COOL[0] + SIDE_COOL[1] * float(smoothstep(SIDE_COOL[2], SIDE_COOL[3], facing))
        h += TONGUE_HEAT * ridge * float(smoothstep(-0.2, 0.4, facing))
        if n.z < -0.2:
            h = min(h, 1.0)  # the underside: the rim's dark red
        values.append(h)
    mats = [(lowest, lit(f"fireball_{index:02x}", index, glow, roughness=0.32 if index < 0x77 else 0.26))
            for lowest, index, glow in FIRE_BANDS]
    band_split(obj, values, mats)
    k.smooth(obj, 75)
    return obj


def core(name):
    cx, cy = CORE
    obj = k.ellipsoid(name, (cx, cy, CORE_Z), (CORE_R, CORE_R, CORE_R), None, 24, 14)
    k.recalc_normals(obj)
    centre = Vector((cx, cy, CORE_Z))
    values = [(v.co - centre).normalized().dot(VIEW) for v in obj.data.vertices]
    mats = [(lowest, lit(f"fireball_core_{index:02x}", index, glow, roughness=0.36)) for lowest, index, glow in
            CORE_BANDS]
    band_split(obj, values, mats)
    k.smooth(obj, 80)
    return obj


def build():
    options = k.args()
    k.reset()
    parts = triangulate([fire(NAME), core(NAME + "_core")])
    bpy.context.view_layer.update()
    if "check" in options:
        check_frames(parts, os.path.join(options["check"], "enemy_K.png"), [(SPRITE, turn(0), "K 171")],
                     move_to_frame=False)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(mk.outdir(options), NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, size=(12, 14), scale=32, distance=0.42)


if __name__ == "__main__":
    build()
