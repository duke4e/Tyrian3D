"""The shots FRUIT's machines launch (enemies the player can shoot, made by their launchers; the game drew them as their
sprites with volume: no generator made models of these sprites and models.cfg had no lines for them), polished
(2026-10-22; nothing replaced). Both come from ground enemies, so they fly on the ground2 layer (drawn on the ground
enemies' layer, height 4: the game centres them in height there).

- green_grape, green_grape_266, green_grape_285 (sheet ' (x27) sprites 247 266 285, 1x1; episode 5's enemy 1261,
  launched every 40 game frames by FRUIT's vent pod (% 195, enemy 1250, fruit_hex_pod; 11 of them, ground events) and
  aimed at the player at launch, speed 3; armour 3). The sprite: a ball 4 pixels wide and 5 high (columns 4-7 of rows
  5-9, the corners cut: rows 5 and 9 two pixels wide), ramp 2's greens, lit at its upper right (0x2e at column 6 of
  row 6) and dark at its lower left (0x27): one of FRUIT's grapes (the grape wing's, polish_grape_wing.py, are the
  same kind of ball, 4 x 4 in ramp 5 lit at the upper right; ' 247 266 285 are, pixel for pixel, the unused ' 190 209
  228 in ramp 5). Its animation 247 247 266 266 285 285 266 266 steps every shade two and four up the ramp: the green
  grape brightens to a cream-white and back, a pulse. A frame model each (no other enemy shows these sprites, launched
  ones included), the same mesh, its materials two and four shades lighter and glowing more (0.14-0.24 in 247 up to
  0.42-0.56 in 285). Built as the grape wing's grapes are (its grape(): a painted icosphere on an ellipsoid, the rim
  darker as the slanted camera sees it, a lit cap where the game's sun puts it, glowing a little in its own colour;
  a finer icosphere, as it is seen alone), an oval grape 4.1 x 5.1 pixels (its long axis up the screen), centred on
  the sprite's ball (y -0.5).

- fruit_bolt, fruit_bolt_281 (sheet % (x25) sprites 279 and 281, 2x2; episode 5's enemies 1263 and 1264, launched
  every 5 game frames by FRUIT's pillars (% 205, enemy 1259, its valve drum on its right: 1263, flying right at
  20 pixels a frame; % 243, 1260, the drum on its left: 1264, flying left), 5 and 3 of them, ground events; armour 20).
  The sprite: a crackling electric bolt across the cell's whole width (24 pixels) in rows 3-13, where the pillar's
  sprite draws its drum (the bolt is launched at the pillar's place and shot out of the drum sideways): three tangled
  strands of white and pale cyan (ramp 8's shades 12-15, 0x8c-0x8f, white 0x7f where they cross) and light blue
  (0x9f), deep blue specks (0x9c, 0x9a), a few lone sparks round them. Its animation alternates 279 and 281 every game
  frame, and 281 is 279 turned 180 degrees in the picture about the strands' middle (column 11.5, row 8: x 0, y 5.5):
  its outline exactly, its shades but for two specks: a frame model (no other enemy shows these sprites). Built as the
  sprite's strands: every pixel a node, its 4-neighbours and its diagonal neighbours (where no 4-neighbour links
  them already) joined by thin glowing tubes, each half in its own pixel's colour, the nodes small beads (lone pixels
  are sparks); the strands wander a little towards and away from the camera (BOLT_WANDER) and are sheared along the
  game camera's line of sight (y - z tan 20) so that every point shows where the sprite draws it; the white strands
  thicker than the blue ones. Every colour glows in itself (0.42-0.62: the bloom and the glow halo add on top). 281's
  model is 279's nodes turned in the picture (x -> -x, y -> 11 - y, z kept) and painted with 281's own pixels: the
  same bounds (the game centres them in height).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (a 1x1 sprite: column c is x = c + 0.5 - 6, row r is y = 6.5 - r; a 2x2: x = c + 0.5 - 12,
y = 13.5 - r).

models.cfg (new): model green_grape (and green_grape_266, _285) enemies/green_grape*.glb, sprite x27 247 green_grape
yaw=0 glow=8:0.2, frame x27 266 green_grape_266, frame x27 285 green_grape_285; model fruit_bolt (and fruit_bolt_281)
enemies/fruit_bolt*.glb, sprite x25 279 fruit_bolt yaw=0 glow=22:0.2:141:0:-5.5 (the strands' middle, 5.5 pixels up),
frame x25 281 fruit_bolt_281.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's silhouette against
its frame), --preview <prefix>, --only <name,...>.
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
from polish_deli_boss import join  # noqa: E402
from polish_balls import Ellipsoid, painted_ball  # noqa: E402
from polish_grape_wing import SUN, TOWARDS_VIEW  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import check_frames, lit, turn  # noqa: E402

VIEW_TILT = 20.0
TAN_TILT = math.tan(math.radians(VIEW_TILT))

# --- ' 247: the green grape -------------------------------------------------------------------------------------------

GRAPE_C = (0.0, -0.5, 0.0)          # the ball's middle (columns 4-7, rows 5-9)
GRAPE_R = (2.05, 2.55, 2.1)         # across, up the screen (5 pixels as the slanted camera sees it), height
# Per frame: (palette index, emission strength) for the rim, the body and the lit cap: the sprite's shades two and
# four up ramp 2 in 266 and 285.
GRAPE_FRAMES = {
    247: ((0x29, 0.14), (0x2b, 0.19), (0x2d, 0.24)),
    266: ((0x2b, 0.26), (0x2d, 0.32), (0x2e, 0.38)),
    285: ((0x2d, 0.42), (0x2e, 0.48), (0x2f, 0.56)),
}
GRAPE_RIM, GRAPE_CAP = 0.3, 0.72    # the grape wing's: the rim where the camera sees the surface edge-on, the lit cap


def green_grape(name, frame):
    """polish_grape_wing.grape()'s painting (the rim darker as the slanted camera sees it, the cap lit by the game's
    sun) on a finer icosphere (subdivisions 3: it is seen alone, not in a bunch)."""
    (dark, dark_glow), (body, body_glow), (light, light_glow) = GRAPE_FRAMES[frame]
    m = {"dark": lit(f"grape{frame}_dark", dark, dark_glow, roughness=0.34),
         "body": lit(f"grape{frame}_body", body, body_glow, roughness=0.3),
         "lit": lit(f"grape{frame}_lit", light, light_glow, roughness=0.26)}
    paint = [(lambda p, n: n.dot(TOWARDS_VIEW), (GRAPE_RIM,), ("dark", "body")),
             (lambda p, n: n.dot(SUN), (GRAPE_CAP,), (None, "lit"))]
    return [painted_ball(name, Ellipsoid(GRAPE_C, GRAPE_R), paint, m, subdivisions=3, smooth_angle=80)]


# --- % 279: the electric bolt -----------------------------------------------------------------------------------------

BOLT_279 = """
.. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. 8c .. .. .. .. .. .. .. .. .. .. .. .. 8e .. .. .. .. ..
8c .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 8d .. ..
.. 8c 8c .. .. .. .. 8f 8f 8f 8d 8f 8f 8f .. .. .. .. .. .. .. .. .. ..
.. .. .. 8d 8f 8f 8f .. .. .. .. .. .. .. 8f .. .. .. .. .. .. .. .. ..
8f 8f 7f .. 7f 8c .. .. .. .. .. .. .. .. .. 8f 8f .. .. .. 9f .. 8f 8f
8d .. .. .. .. .. 8c 8c 9f .. .. .. 8c 7f 8c 8c .. 8f 9f 7f 8f 9f 9f ..
.. .. 8d .. 9f 9c 9f .. 8c 7f 8c 8d .. .. .. 9f 8d 8c 8f 8f .. 8d .. 9c
.. .. .. 9f .. .. .. .. .. .. .. 9f 9f 7f 9f .. .. .. 8c 8c .. .. .. 8d
.. 9f 7f .. .. .. .. .. 8e .. .. .. .. .. .. .. .. .. .. .. 8c 8d .. ..
9c .. .. .. .. .. .. .. .. .. .. .. .. .. 8e .. .. .. .. .. .. .. 8c 8c
.. .. 8e .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..
"""
BOLT_281 = """
.. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 8e .. ..
8c 8c .. .. .. .. .. .. .. 8e .. .. .. .. .. .. .. .. .. .. .. .. .. 9a
.. .. 8d 8c .. .. .. .. .. .. .. .. .. .. .. 8e .. .. .. .. .. 7f 9f ..
8d .. .. .. 8c 8c .. .. .. 9f 7f 9f 9f .. .. .. .. .. .. .. 9f .. .. ..
9a .. 8d .. 8f 8f 8c 8d 9f .. .. .. 8d 8c 7f 8c .. 9f 9f 9f .. 8d .. ..
.. 9f 9f 8f 7f 9f 8f .. 8c 8c 7f 8c .. .. .. 9f 8c 8c .. .. .. .. .. 8d
8f 8f .. 9f .. .. .. 8f 8f .. .. .. .. .. .. .. .. .. 8c 7f .. 7f 8f 8f
.. .. .. .. .. .. .. .. .. 8f .. .. .. .. .. .. .. 8f 8f 8f 8d .. .. ..
.. .. .. .. .. .. .. .. .. .. 8f 8f 8f 8d 8f 8f 8f .. .. .. .. 8c 8c ..
.. .. 8d .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. 8c
.. .. .. .. .. 8e .. .. .. .. .. .. .. .. .. .. .. .. 8c .. .. .. .. ..
"""
BOLT_MIDDLE_Y = 5.5     # the strands' middle (row 8), about which 281 is 279 turned
# Each colour: its emission strength (in its own colour) and the strands' radius through its pixels.
BOLT_COLOURS = {0x7f: (0.62, 0.46), 0x8f: (0.6, 0.46), 0x8e: (0.56, 0.43), 0x8d: (0.52, 0.42), 0x8c: (0.48, 0.4),
                0x9f: (0.5, 0.38), 0x9c: (0.46, 0.36), 0x9a: (0.42, 0.36)}
SPARK_R = 0.46          # a lone pixel's bead
BOLT_WANDER = (0.65, 0.7, 0.9, 0.28, 1.9, -0.45, 1.0)   # z = a sin(b x + c y) + d sin(e x + f y + g)
TUBE_SEGMENTS, BEAD_SEGMENTS, BEAD_RINGS = 6, 8, 5


def grid(art):
    return [[None if t == ".." else int(t, 16) for t in line.split()] for line in art.strip("\n").splitlines()]


def wander(x, y):
    a, b, c, d, e, f, g = BOLT_WANDER
    return a * math.sin(b * x + c * y) + d * math.sin(e * x + f * y + g)


def bolt_nodes(turned=False):
    """The bolt's nodes: {(column, row): picture point (x, y, z)} of 279's pixels, turned 180 degrees about the
    strands' middle for 281 (the node at 279's (c, r) goes to (23 - c, 16 - r), keeping its z)."""
    nodes = {}
    for r, row in enumerate(grid(BOLT_279)):
        for c, index in enumerate(row):
            if index is None:
                continue
            x, y = c + 0.5 - 12, 13.5 - r
            z = wander(x, y)
            if turned:
                nodes[(23 - c, 16 - r)] = (-x, 2 * BOLT_MIDDLE_Y - y, z)
            else:
                nodes[(c, r)] = (x, y, z)
    return nodes


def bolt_edges(nodes):
    """4-neighbours, and diagonal neighbours that no 4-neighbour of both links already."""
    edges = []
    for (c, r) in sorted(nodes):
        for dc, dr in ((1, 0), (0, 1)):
            if (c + dc, r + dr) in nodes:
                edges.append(((c, r), (c + dc, r + dr)))
        for dc in (1, -1):
            other = (c + dc, r + 1)
            if other in nodes and (c + dc, r) not in nodes and (c, r + 1) not in nodes:
                edges.append(((c, r), other))
    return edges


def seen(p):
    """A picture point (x, y, z) moved along the game camera's line of sight so that it shows at (x, y)."""
    x, y, z = p
    return Vector((x, y - z * TAN_TILT, z))


def bead(name, centre, radius, mat):
    return k.smooth(k.ellipsoid(name, tuple(centre), (radius,) * 3, mat, BEAD_SEGMENTS, BEAD_RINGS), 80)


def fruit_bolt(name, frame):
    art = grid(BOLT_279 if frame == 279 else BOLT_281)
    nodes = bolt_nodes(turned=frame == 281)
    mats = {index: lit(f"bolt_{index:02x}", index, glow, roughness=0.35) for index, (glow, _) in BOLT_COLOURS.items()}
    edges = bolt_edges(nodes)
    linked = {n for e in edges for n in e}
    parts = []
    for (c, r) in sorted(nodes):
        index = art[r][c]
        radius = BOLT_COLOURS[index][1] if (c, r) in linked else SPARK_R
        parts.append(bead(f"{name}_n{c}_{r}", seen(nodes[(c, r)]), radius * 1.04, mats[index]))
    for a, b in edges:
        pa, pb = Vector(nodes[a]), Vector(nodes[b])
        mid = (pa + pb) / 2
        for end, p in ((a, pa), (b, pb)):
            index = art[end[1]][end[0]]
            radius = BOLT_COLOURS[index][1]
            # half the link, in its own pixel's colour, straight in the picture (sheared as a whole)
            pts = [seen(tuple(p)), seen(tuple(mid))]
            parts.append(mk.tube(f"{name}_e{a[0]}_{a[1]}_{b[0]}_{b[1]}_{end[0]}", pts, radius, mats[index],
                                 segments=TUBE_SEGMENTS, cap=False))
    for obj in parts:
        k.smooth(obj, 80)
    return [join(parts, name)]


# --- Build ------------------------------------------------------------------------------------------------------------

MODELS = [
    # name, sheet file, 2x2, make, frame
    ("green_grape", "x27", False, lambda name: green_grape(name, 247), 247),
    ("green_grape_266", "x27", False, lambda name: green_grape(name, 266), 266),
    ("green_grape_285", "x27", False, lambda name: green_grape(name, 285), 285),
    ("fruit_bolt", "x25", True, lambda name: fruit_bolt(name, 279), 279),
    ("fruit_bolt_281", "x25", True, lambda name: fruit_bolt(name, 281), 281),
]


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sheet, large, make, frame in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        objects = make(name)
        triangulate(objects)
        bpy.context.view_layer.update()
        if "check" in options:
            label = ("' " if sheet == "x27" else "% ") + str(frame)
            check_frames(objects, os.path.join(options["check"], f"enemy_{sheet}.png"), [(frame, turn(0), label)],
                         move_to_frame=False, large=large)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, objects, os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options:
            if large:
                mk.preview(options["preview"] + name, objects, size=(24, 28), scale=16, distance=0.75)
            else:
                mk.preview(options["preview"] + name, objects, size=(12, 14), scale=32, distance=0.42)


if __name__ == "__main__":
    build()
