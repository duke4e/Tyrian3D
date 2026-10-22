"""The two shots of FRUIT that had no model and were missing from the catalogue (enemies the player can shoot, made by
their launchers when FRUIT's events give them a launch type or frequency (event 58 / event 31): catalog.json and the
launched list find launches only in the enemy data, so it missed both; the game drew them as their sprites with
volume), polished (2026-10-22, round 37; nothing replaced: no generator made models of these sprites and models.cfg had
no lines for them).

- fruit_flame, fruit_flame_245 (sheet ' (x27) sprites 207 and 245, 2x2; episode 5's enemy 1244, armour 20, falling
  down the screen 5 pixels a game frame, no aim): the pale green flame FRUIT's pineapple boss fires all fight long, its
  two barrels (' 270 and 278, enemies 1289 and 1293, ground events at t5000; their elaunchtype is 1244, and event 31
  sets their launch frequency to 10 again and again from t5119) and the lemon beetle's lower pieces (' 92 beside 94,
  enemies 1242 and 1243 of polish_lemon_beetle.py's beetle, link 15: event 31 gives them launch frequency 20 at t1105,
  1445, 2045, 3705 ...). From the barrels it flies on the ground2 layer, from the beetle on the top layer; episode 6's
  THE CORE (FRUIT's boss block) has the barrels too. The sprite (columns 8-16 of rows 4-24): a flame falling with its
  tongues trailing up the screen: a body of fire (rows 13-24, 6-8 pixels wide, rounded to a point at row 24) in ramp 2's
  pale greens (0x2c, 0x2d, 0x2e: shades 12-14) with cream sparks (ramp 1, 0x1d, 0x1e), and two tongues above it, a tall
  one (2-3 pixels wide, its tip at row 4, a cream core 0x1e down rows 6-8) and a short one beside it (one or two pixels,
  rows 7-12). Its animation alternates 207 and 245 every game frame: 245 swaps the tongues, the tall one at the right
  (column 13), the short one at the left (columns 10-11), the body a pixel further right (columns 9-16): not 207
  mirrored pixel for pixel (its body's shades differ; outline match 76 %), so a frame model of its own (no other enemy
  shows ' 207 or 245, launched ones included; no other sprite is their pixels mirrored, turned or in other ramps).
  Built as FRUIT's and the fire family's flames are (polish_flame_drop.py's fire_body(), Outline and Heat): the body a
  body of fire round in section along the screen's y (its half-widths the sprite's rows, smoothed, closing to a point
  at its top under the tongues and rounded at its foot), each tongue a thin body of its own from its tip down into the
  body (the sprite's runs of pixels above the body followed up row by row); painted with the sprite's colours on one
  heat scale (0x2c 12, 0x2d 13, 0x2e 14, 0x1d 14.4, 0x1e 15), smoothed, cooler where the surface turns away from the
  camera, in bands of ramp 2 (0x2a under it, 0x2b-0x2e) and the cream 0x1e for the hottest, each band glowing in its own
  colour, more the hotter (0.16-0.5), the hottest parts swelling a little (glints as on molten glass).

- purple_grape, purple_grape_209, purple_grape_228 (sheet ' sprites 190 209 228, 1x1; episode 5's enemy 1245, armour
  2): the grape FRUIT's grape wings (' 130 beside 132, enemies 1227 and 1228, sky events) launch every 15 game frames
  when event 58 gives their link launch type 1245 and event 31 frequency 15 (t850-920, 1020-1070, 1290-1360, 2490-2560,
  2590-2660, 3490-3560, 3670-3870: links 10, 11, 12); 1245's own launch type 3 with no launch of its own makes the game
  aim it at the player at launch, speed 3 (tyrian2.c: a launched enemy whose launchtype is under 90). On the sky layer,
  as its launchers. The sprite is, pixel for pixel, ' 247 266 285 (the green grape of FRUIT's vent pods,
  polish_launched_fruit.py's green_grape) in ramp 5's purples (the grape wing's grapes' colours): a ball 4 pixels wide
  and 5 high, lit at its upper right (0x5e), dark at its lower left (0x57); its animation 190 190 209 209 228 228 steps
  every shade two and four up the ramp, a grape brightening to a pale lilac white and back to dark (a ramp, not the
  green grape's pulse). (polish_launched_fruit.py calls 190 209 228 unused: enemy 1245 shows them.) A frame model each
  (no other enemy shows these sprites), built by polish_launched_fruit.green_grape() itself (the same mesh as the green
  grape, the grape wing's painting: the rim darker as the slanted camera sees it, a lit cap where the game's sun puts
  it) in ramp 5, glowing faintly in its own colours as the green one does (0.14-0.24 in 190 up to 0.42-0.56 in 228).
  color=sprite on the green grape would follow the ramp but not its emission (green glow on a purple grape): its own
  models instead.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (a 2x2 sprite: column c is x = c + 0.5 - 12, row r is y = 13.5 - r; a 1x1 sprite x = c + 0.5 - 6,
y = 6.5 - r). The game centres these models in height: each frame model has its frame's own bounds in x and y and the
same bounds in z (FLAME_Z: both flames stretched to it). Every mesh is triangulated (polish_k_pod.triangulate) and a
model's parts joined; no random numbers, no booleans (the same output every run, with and without --check).

models.cfg (new): model fruit_flame enemies/fruit_flame.glb, model fruit_flame_245 enemies/fruit_flame_245.glb, sprite
x27 207 fruit_flame yaw=0 glow=14:0.25:45:0:4 (the flame's middle, 4 pixels down the screen), frame x27 245
fruit_flame_245; model purple_grape (and purple_grape_209, _228) enemies/purple_grape*.glb, sprite x27 190 purple_grape
yaw=0 glow=8:0.2, frame x27 209 purple_grape_209, frame x27 228 purple_grape_228.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's silhouette
against its frame), --preview <prefix>, --only <name,...>.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_launched_fruit as lf  # noqa: E402  (its green grape; its build() runs only as a script)
from polish_deli_boss import join  # noqa: E402
from polish_flame_drop import Heat, Outline, fire_body  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import check_frames, lit, turn, vertex_bounds  # noqa: E402

# --- ' 207 / 245: the pale green flame -------------------------------------------------------------------------------

FLAME_ART = {207: """
................................................
................................................
................................................
................................................
........................2d......................
........................2d......................
......................2d1e......................
......................2d1e..2d..................
......................2d1e..2d..................
......................2d2d....2d................
......................2c2d..2d2d................
....................2c2d2d..2d1d................
....................2d2d2c..2c1d................
..................2c2d2e2d1e2c2d................
..................2c2d2d2c2e2d2e................
..................2d2d2c2c2d2c2e................
................2d2d2e2c2c2d2c2d................
................2d2c2e2c2d2d2c2d................
..................2c2d2c2e2c2d..................
..................2d2c2d2d2c2c..................
..................1d1d2e2d2d2c..................
..................2d2c2d2e2d2c..................
....................2c2c2d2c....................
....................2d2c2c2c....................
........................2c......................
................................................
................................................
................................................
""", 245: """
................................................
................................................
................................................
................................................
..........................2d....................
..........................2d....................
..........................1e2d..................
......................2d..1e2d..................
......................2d..1e2d..................
....................2d....2d2d..................
....................2d2d..2d2c..................
....................1d2d..2d2d2c................
..................1d2c..2c2d2d..................
..................2d2c1e2d2e2d2c................
..................2e2d2e2c2d2d2c................
..................2e2c2d2c2c2d2d................
..................2d2c2d2c2c2e2d2d..............
..................2d2c2d2d2c2e2c2d..............
....................2d2c2e2c2d2c................
....................2c2c2d2d2c2d................
....................2c2d2d2e1d1d................
....................2c2d2e2d2c2d................
......................2c2d2c2c..................
......................2c2c2c2d..................
........................2c......................
................................................
................................................
................................................
"""}
TOP = 14.0                                   # the y of a 2x2 sprite's top edge
HEAT_OF = {0x2c: 12.0, 0x2d: 13.0, 0x2e: 14.0, 0x1d: 14.4, 0x1e: 15.0}   # the sprite's colours on one heat scale
# (lowest heat, palette index, glow): ramp 2's pale greens from under the flame up, the cream 0x1e the hottest.
FLAME_BANDS = [(-99.0, 0x2a, 0.16), (11.2, 0x2b, 0.2), (12.15, 0x2c, 0.26), (12.8, 0x2d, 0.33), (13.55, 0x2e, 0.41),
               (14.35, 0x1e, 0.5)]
BODY_DEPTH = (0.74, 0.56)                    # the bodies' half-depths above and below the axis, times the half-width
TONGUE_DEPTH = (0.8, 0.62)
COOL = 0.9                                   # this much cooler where the surface turns away from the camera (1 - n.z)
UNDER = 10.0                                 # the heat of the underside (its lowest band)
SWELL = (0.3, 13.2)                          # how far the hottest parts swell out, and from what heat
TONGUE_SINK = 2                              # rows a tongue reaches down into the body
BODY_POINT = 2.4                             # the body closes this far over its top row, round under the tongues
BODY_RES = (0.45, (18, 8))                   # rings' spacing and segments (upper, lower half) of the body
TONGUE_RES = (0.4, (12, 6))                  # and of the tongues
FLAME_Z = (-2.4, 3.2)                        # both frames' bounds in height (the game centres the model in height)


def grid(art):
    return [[None if line[2 * c:2 * c + 2] == ".." else int(line[2 * c:2 * c + 2], 16) for c in range(len(line) // 2)]
            for line in art.split()]


def runs(row):
    """The row's runs of pixels: (first column, column after the last)."""
    out, c = [], 0
    while c < len(row):
        if row[c] is None:
            c += 1
            continue
        c0 = c
        while c < len(row) and row[c] is not None:
            c += 1
        out.append((c0, c))
    return out


def split_flame(rows):
    """The body's first row (the rows from the bottom up while each is one run of pixels) and the tongues above it, each
    {row: (c0, c1)}: every run above the body joins the tongue whose run in the row below it overlaps or touches."""
    filled = [r for r, row in enumerate(rows) if any(v is not None for v in row)]
    r = filled[-1]
    while r >= filled[0] and len(runs(rows[r])) == 1:
        r -= 1
    body_top = r + 1
    tongues = []
    for r in range(body_top - 1, filled[0] - 1, -1):
        for c0, c1 in runs(rows[r]):
            home = None
            for t in tongues:
                if min(t) == r + 1 and c0 <= t[r + 1][1] and t[r + 1][0] <= c1:
                    home = t
                    break
            if home is None:
                home = {}
                tongues.append(home)
            home[r] = (c0, c1)
    return body_top, tongues


def flame(name, frame):
    rows = grid(FLAME_ART[frame])
    heat_rows = [[None if v is None else HEAT_OF[v] for v in row] for row in rows]
    heat = Heat(heat_rows, TOP)
    mats = [(lowest, lit("flame_%02x" % index, index, glow, roughness=0.3 if index != 0x2a else 0.4))
            for lowest, index, glow in FLAME_BANDS]

    def heat_of(x, y, n):
        return heat(x, y) - COOL * (1.0 - n.z) if n.z > -0.05 else UNDER
    body_top, tongues = split_flame(rows)
    body_rows = [row if r >= body_top else [None] * len(row) for r, row in enumerate(rows)]
    parts = [fire_body(name + "_body", Outline(body_rows, TOP, point=BODY_POINT), heat, mats, depth=BODY_DEPTH,
                       swell=SWELL[0], swell_from=SWELL[1], step=BODY_RES[0], segments=BODY_RES[1], heat_of=heat_of)]
    for i, t in enumerate(tongues):
        bottom = max(t)
        c0, c1 = t[bottom]
        t_rows = [[None] * len(rows[0]) for _ in rows]
        for r, (a, b) in t.items():
            for c in range(a, b):
                t_rows[r][c] = rows[r][c]
        for r in range(body_top, body_top + TONGUE_SINK):   # down into the body, as wide as its lowest run
            for c in range(c0, c1):
                t_rows[r][c] = rows[r][c] if rows[r][c] is not None else rows[bottom][c]
        outline = Outline(t_rows, TOP, point=0.55, bottom_round=((0.3, 0.8), (0.45, 0.45), (0.55, 0.0)))
        parts.append(fire_body("%s_tongue%d" % (name, i), outline, heat, mats, depth=TONGUE_DEPTH, swell=SWELL[0] * 0.5,
                               swell_from=SWELL[1], step=TONGUE_RES[0], segments=TONGUE_RES[1], heat_of=heat_of))
    triangulate(parts)
    obj = join(parts, name)
    # The same bounds in height for both frames: stretched to FLAME_Z about the axis.
    low, high = vertex_bounds([obj])
    up, down = FLAME_Z[1] / high.z, FLAME_Z[0] / low.z
    for v in obj.data.vertices:
        v.co.z *= up if v.co.z > 0 else down
    obj.data.update()
    return [obj]


# --- ' 190: the purple grape (the green grape's mesh and painting in ramp 5) ------------------------------------------

# Per frame: (palette index, emission strength) for the rim, the body and the lit cap, as the green grape's 247 266 285.
PURPLE_FRAMES = {
    190: ((0x59, 0.14), (0x5b, 0.19), (0x5d, 0.24)),
    209: ((0x5b, 0.26), (0x5d, 0.32), (0x5e, 0.38)),
    228: ((0x5d, 0.42), (0x5e, 0.48), (0x5f, 0.56)),
}


def purple_grape(name, frame):
    lf.GRAPE_FRAMES.update(PURPLE_FRAMES)
    return lf.green_grape(name, frame)


# --- Build ------------------------------------------------------------------------------------------------------------

MODELS = [
    # name, 2x2, make, frame
    ("fruit_flame", True, lambda name: flame(name, 207), 207),
    ("fruit_flame_245", True, lambda name: flame(name, 245), 245),
    ("purple_grape", False, lambda name: purple_grape(name, 190), 190),
    ("purple_grape_209", False, lambda name: purple_grape(name, 209), 209),
    ("purple_grape_228", False, lambda name: purple_grape(name, 228), 228),
]


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, large, make, frame in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        objects = make(name)
        triangulate(objects)
        bpy.context.view_layer.update()
        if "check" in options:
            check_frames(objects, os.path.join(options["check"], "enemy_x27.png"), [(frame, turn(0), "' %d" % frame)],
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
