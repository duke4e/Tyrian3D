"""The solid shots that enemies launch (enemies the player can shoot, made by their launchers: catalog.json lists none
of them; the game drew them as pixelated stand-ins built from the sprite), polished (2026-10-21; nothing replaced: no
generator made models of these sprites, and models.cfg had no lines for them). polish_launched_flames.py builds the
glowing ones (and has the helpers used here). Launched enemies keep their launcher's layer: most of these come from
ground turrets (drawn on the ground enemies' layer, height 4: the game centres them in height there), some from sky
launchers.

- steel_needle (sheet S sprite 171, 1x1; enemy 455 of episodes 1-3 and 5, launched by D 241, S 269 (ground) and D 79,
  D 117 (sky) in ** ALE **, AST ROCK, AST. CITY, ASTEROID?, BONUS and MINEMAZE, and aimed at the player at launch,
  speed 4). The sprite: a grey steel needle, 12 pixels long, 5 wide at its middle (rows 5-8 of S 190), 3 (rows 3-4,
  9-10) and 1 at its points, a light stripe down its middle (0x0b-0x0d) between darker sides (0x06, 0x08). Its frames
  171 190 209 228 (two game frames each) are the needle turned 45 degrees a frame clockwise: 171 from the upper left
  (-45), 190 up the screen, 209 to the upper right, 228 across (209 is 171 mirrored). One model, turned by models.cfg:
  yaw=frames:16:-56.25 (22.5 degrees a game frame from -56.25, so each sprite's heading is the middle of its two
  frames; it looks the same turned half round). Built as a six-sided steel spindle, a ridge along its top, its facets
  flat (they glint as it turns), the ridge light, the underside darker.

- twin_pellets (sheet D sprite 228, 1x1; enemy 532 of episodes 1 and 2, launched by D 79 (ornament) in ASTCITY and
  ASTEROID?, aimed at the player at launch, speed 4). The sprite: two glossy steel blue balls (ramp 3), each 6 pixels
  across with its outline, side by side and touching (columns 0-5 and 6-11 of rows 4-9). Its frames 228 247 266 285
  304 247 (three game frames each) are the pair turning about the screen's up axis: 247 brings them to 2 pixels either
  side, 266 overlaps them with the left one in front (the one behind darker, its right side showing), 285 hides one
  behind the other, 304 has the right one in front, 247 again, and 228 the pair swapped (the balls are alike): half a
  turn in 18 game frames. One model rolled by models.cfg: roll=frames:36 (a roll about the model's nose, +Y, up the
  screen at yaw=0, 10 degrees a game frame; positive rolls raise the model's left side towards the camera, as 266
  shows; the sprite's steps are uneven (it lingers where the balls overlap), the model's even, its rest 10 degrees
  back so that it misses no frame by more than about 20 degrees). Built as two balls, 5.6 across, a hair apart at the
  middle, a
  dark seam round each where it meets the plane of the pair (seen on its edge as frame 228's outline; it shows the
  tumble), glossy, glowing a little in their own blue so that the camera's side of them doesn't read black.

- white_dart, white_dart_190, white_dart_209 (sheet D sprites 171 190 209, 1x1; enemies 543 544 551 of episodes 1, 3
  and 5, launched by M 83, M 87 (armour_dome) and S 267 (carrier_launcher) in AST ROCK, AST. CITY, ASTEROID1 and
  ASTEROID2, flying down the screen: (-2, 5), (2, 5), or (0, 1) speeding up). The sprite: a white dart, its nose down
  the screen: a body 3 pixels wide with a light stripe down its middle (0x0d) and its outline (0x20), two sets of
  diamond fins (rows 0-4 and 5-9, 9 pixels across at rows 1-2 and 6-7, white 0x0e and grey 0x0b), a glowing band
  round the body near its nose (row 10) and a dark point (row 12). Its frames 171 190 209 190 (two game frames each,
  171 once more) change only the band: 0x74 0x78 0x74 (dark red), 0x76 0x7a 0x76, 0x7a 0x7e 0x7a (orange-yellow): a
  light pulsing. A frame model each (no other enemy shows these sprites), the same mesh, the band's colours and glow
  rising. D 171 is, pixel for pixel, sheet ^ (x5e) 171: UNDERDELI's launched shot (episode 4's enemies 41 and 42,
  frames 171 999, falling (0, 4)), which white_dart can show too. The model is authored with its nose up the screen,
  for yaw=velocity (it points along its path: models.cfg's yaw is 180, down the screen, until it moves). Built as a
  turned body (a blunt rear with a dark nozzle, an ogive nose with a dark point), the band a glowing ring round it,
  and cruciform fins (the sprite's two diamond fins either side and two smaller ones above and below), their rims
  rounded.

- ice_spike (sheet D sprite 191, 2x2: 7 x 28 pixels in the 24 x 28 cell, columns 8-14; enemy 463 of episodes 1-3 and
  5 and episode 3's 86, launched by D 275 (cage_turret) and 7 207 (ice_drill_arm) in AST ROCK, AST. CITY, ASTCITY,
  ASTEROID1, ASTEROID2, ASTEROID? and CAMANIS, falling (0, 4); not animated). The sprite: a long shard of ice, white
  in its lower middle (0x3f), light blue (0x3d, 0x3e) up its upper part and along its sides, dark blue (0x3a) down its
  left edge, rounded to a point at the bottom (rows 24-27) and broken at the top into three splinters (column 9 up to
  row 0, column 13 up to row 1, columns 11-12 up to row 3). Built as a six-sided crystal lying along the screen (its
  flat top face between two slanted faces either side), ending below in a six-sided point and above in a slanted
  break from which three thin crystals stick out (the splinters), painted by its facets (the top face white, the
  sun's side light, the far side darker) and along its length (whitest in its lower middle, streaked in its upper
  part, darker into its point), glossy, glowing a little in its own light blue (ice catches the light).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (a 1x1 sprite's pixel 6, 7: column c is x = c + 0.5 - 6, row r is y = 6.5 - r; D 191's pixel 12, 14:
x = c + 0.5 - 12, y = 13.5 - r). The game centres these models in height.

models.cfg (new): model steel_needle enemies/steel_needle.glb, sprite s 171 steel_needle yaw=frames:16:-56.25; model
twin_pellets enemies/twin_pellets.glb, sprite d 228 twin_pellets yaw=0 roll=frames:36 height=3 (the game lifts a
model whose turned bounds reach below 0.3 over the ground: on the ground enemies' layer, 4, the rolling pair's would,
so it would bob; 3 higher it never does); model white_dart (and white_dart_190, _209) enemies/white_dart*.glb, sprite
d 171 white_dart yaw=velocity glow=6:0.3:120:-0.5:3.5 (the band), frame d 190 white_dart_190, frame d 209
white_dart_209; model ice_spike enemies/ice_spike.glb, sprite d 191 ice_spike yaw=0.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes against each
frame, the model turned or rolled as the frame shows it), --preview <prefix>, --only <name,...>.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import check_frames, lit, smoothstep, turn, vertex_normals  # noqa: E402


def plain(name, index, metallic=0.5, roughness=0.3):
    return k.material(name, palette=index, metallic=metallic, roughness=roughness)


def facet_ring(y, half_width, half_height, x=0.0, z=0.0, sides=6, power=2.0, start=90.0):
    """A cross-section in the XZ plane at y: a polygon of `sides` corners on an ellipse (a superellipse for power > 2),
    the first corner at `start` degrees (90: on top, a ridge)."""
    pts = []
    for j in range(sides):
        a = math.radians(start + 360.0 * j / sides)
        c, s = math.cos(a), math.sin(a)
        pts.append(Vector((x + math.copysign(abs(c) ** (2 / power), c) * half_width, y,
                           z + math.copysign(abs(s) ** (2 / power), s) * half_height)))
    return pts


def flat_shade(obj, angle=30.0):
    """Facets flat, smooth along a facet's length (shade_smooth_by_angle keeps edges sharper than angle)."""
    return k.smooth(obj, angle)


# --- S 171: the spinning steel needle ---------------------------------------------------------------------------------

# The spindle: its half-length, its half-width at the middle and its profile (r = width * (1 - (|y| / length) ^ a) ^ b),
# the cross-section's height (times the width), the rings along it.
STEEL_NEEDLE = (6.15, 2.5, 1.6, 1.1)
STEEL_DEPTH = 0.72
STEEL_RINGS = 24
# The paint by the facets' normals: the ridge and the two facets either side of it light, the lower facets darker.
STEEL = {"ridge": 0x0d, "top": 0x0b, "side": 0x09, "under": 0x06}


def steel_needle(name):
    length, width, a, b = STEEL_NEEDLE
    ys = [-length + 2 * length * i / STEEL_RINGS for i in range(1, STEEL_RINGS)]
    ys = sorted(set(ys) | {-length + d for d in (0.1, 0.3)} | {length - d for d in (0.1, 0.3)})
    rings = []
    for y in ys:
        r = width * max(0.0, 1 - (abs(y) / length) ** a) ** b
        # (the side corners of a section with a corner on top lie at 30 degrees: widened so that they reach r)
        rings.append(facet_ring(y, max(r, 0.02) / math.cos(math.radians(30)), max(r, 0.02) * STEEL_DEPTH))
    obj = k.loft(name, rings, None, start_point=(0, -length, 0), end_point=(0, length, 0))
    mats = {key: plain(f"steel_{key}", index, metallic=0.6, roughness=0.26 if key != "under" else 0.4)
            for key, index in STEEL.items()}
    # The ridge: a thin light band along the top corner; the upper facets light; the lower ones darker.
    values = []
    for v, n in zip(obj.data.vertices, vertex_normals(obj)):
        values.append(n.z)
    band_split(obj, values, [(-99.0, mats["under"]), (-0.25, mats["side"]), (0.3, mats["top"]),
                             (0.93, mats["ridge"])])
    flat_shade(obj, 25)
    return [obj]


def steel_frames():
    return [(171, turn(-45), "S 171"), (190, turn(0), "S 190"), (209, turn(45), "S 209"), (228, turn(90), "S 228")]


# --- D 228: the tumbling pair of pellets ------------------------------------------------------------------------------

PELLET_X, PELLET_R = 2.95, 2.8
SEAM_WIDTH = 0.32    # the dark seam round each ball (pixels either side of the pair's plane)
# The pair at rest is rolled this much (degrees; the game rolls it 0-170 on top): the sprite's steps are uneven (it
# lingers where the balls overlap), and starting 10 degrees back halves the largest miss of an even roll.
PELLET_REST_ROLL = -10.0
PELLET = {"body": (0x3b, 0.12, 0x3c), "seam": (0x33, 0.0, None)}


def twin_pellets(name):
    objects = []
    body_index, body_glow, glow_index = PELLET["body"]
    body = lit("pellet_body", body_index, body_glow, roughness=0.2, metallic=0.35, emission_index=glow_index)
    seam = lit("pellet_seam", PELLET["seam"][0], 0.0, roughness=0.45, metallic=0.2)
    for side in (-1, 1):
        ball = mk.ball(f"{name}_{'lr'[side > 0]}", (side * PELLET_X, 0.0, 0.0), (PELLET_R,) * 3, None, segments=28,
                       rings=16)
        values = [abs(v.co.z) for v in ball.data.vertices]
        band_split(ball, values, [(-99.0, seam), (SEAM_WIDTH, body)])
        k.smooth(ball, 70)
        objects.append(ball)
    mk.transform(objects, roll(PELLET_REST_ROLL))
    return objects


def roll(degrees):
    """models.cfg's roll as the game turns the model: right-handed about +Y (the left side rising)."""
    return Matrix.Rotation(math.radians(degrees), 4, "Y")


def pellet_frames():
    # The middle of each sprite's three game frames at 10 degrees a frame.
    return [(228, roll(10), "D 228"), (247, roll(40), "D 247"), (266, roll(70), "D 266"), (285, roll(100), "D 285"),
            (304, roll(130), "D 304")]


# --- D 171: the white dart -------------------------------------------------------------------------------------------

# Built as the sprite draws it (nose down, its axis at x = DART_X), then turned half round (HALF_TURN: nose up, for
# yaw=velocity, its axis at x = 0.5).
DART_X = -0.5
HALF_TURN = Matrix.Rotation(math.pi, 4, "Z")
# The body's profile (y, radius) from its nose's point up to its rear; the nozzle (y from, radius); the band (y range,
# its radius); the fins' plans (x from the axis, y) for the two sets, their thickness, the upper and lower fins' share
# of the side fins' span.
DART_BODY = [(-6.05, 0.0), (-5.95, 0.55), (-5.75, 0.98), (-5.45, 1.38), (-5.05, 1.72), (-4.55, 1.97), (-4.0, 2.08),
             (-3.0, 2.1), (2.0, 2.1), (6.3, 2.1), (6.6, 2.02), (6.85, 1.8), (7.0, 1.5)]
DART_NOZZLE = (6.6, 1.25)
DART_TIP = -5.55      # below this the point is dark
DART_BAND = (-4.05, -2.95, 2.22)
FINS = [
    [(1.7, 7.0), (3.6, 7.0), (4.6, 6.05), (4.6, 4.15), (3.3, 3.05), (1.7, 2.75)],
    [(1.7, 2.3), (3.3, 2.0), (4.6, 0.95), (4.6, -0.95), (3.3, -2.0), (1.7, -2.3)],
]
FIN_THICK, FIN_UPRIGHT = 0.7, 0.78
DART = {"body": 0x0c, "stripe": 0x0e, "side": 0x0a, "under": 0x08, "fin": 0x0e, "fin_edge": 0x0b, "dark": 0x20}
# The band per frame: its sides and its crown (palette index, emission strength).
DART_FRAMES = {171: ((0x74, 0.2), (0x78, 0.3)), 190: ((0x76, 0.3), (0x7a, 0.42)), 209: ((0x7a, 0.42), (0x7e, 0.58))}


def inset(outline, d):
    """A convex outline (counter-clockwise) with every edge moved d inwards."""
    n = len(outline)
    lines = []
    for i in range(n):
        (x0, y0), (x1, y1) = outline[i], outline[(i + 1) % n]
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        lines.append((x0 - dy / length * d, y0 + dx / length * d, dx, dy))
    out = []
    for i in range(n):
        px, py, ux, uy = lines[i - 1]
        qx, qy, vx, vy = lines[i]
        det = ux * vy - uy * vx
        t = ((qx - px) * vy - (qy - py) * vx) / det
        out.append((px + ux * t, py + uy * t))
    return out


# The fins' rounded rim: (z as a share of the half-thickness, how far in (pixels)), from the bottom face up.
FIN_RIM = [(-1.0, 0.22), (-0.82, 0.064), (-0.37, 0.0), (0.37, 0.0), (0.82, 0.064), (1.0, 0.22)]


def fin(name, plan, axis_x, face, edge):
    """A fin: the plan (x out from the axis, y) FIN_THICK thick about z = 0, its rim rounded (rings of the outline set
    in, lofted: no modifier, the same every run); its faces `face`, its rim `edge`."""
    outline = [(axis_x + x, y) for x, y in plan]
    if sum(outline[i][0] * outline[(i + 1) % len(outline)][1] - outline[(i + 1) % len(outline)][0] * outline[i][1]
           for i in range(len(outline))) < 0:
        outline.reverse()
    rings = [[Vector((x, y, share * FIN_THICK / 2)) for x, y in inset(outline, d)] for share, d in FIN_RIM]
    bottom, top = (sum((Vector((x, y, 0)) for x, y in outline), Vector()) / len(outline) + Vector((0, 0, z))
                   for z in (-FIN_THICK / 2, FIN_THICK / 2))
    obj = k.loft(name, rings, None, start_point=bottom, end_point=top)
    band_split(obj, [abs(n.z) for n in vertex_normals(obj)], [(-99.0, edge), (0.7, face)])
    k.smooth(obj, 40)
    return obj


def white_dart(name, frame):
    m = {key: plain(f"dart_{key}", index, metallic=0.25 if key != "dark" else 0.1,
                    roughness=0.32 if key != "dark" else 0.2) for key, index in DART.items()}
    (side_index, side_glow), (crown_index, crown_glow) = DART_FRAMES[frame]
    band_side = lit(f"dart{frame}_band", side_index, side_glow, roughness=0.25)
    band_crown = lit(f"dart{frame}_crown", crown_index, crown_glow, roughness=0.22)
    objects = []
    # The body, turned about its axis.
    rings = [k.ring(y, r, r, 24, x=DART_X) for y, r in DART_BODY if r > 0]
    body = k.loft("body", rings, None, start_point=(DART_X, DART_BODY[0][0], 0),
                  end_point=(DART_X, DART_BODY[-1][0], 0))
    values = []
    for v, n in zip(body.data.vertices, vertex_normals(body)):
        y = v.co.y
        if y < DART_TIP or (y > DART_NOZZLE[0] and math.hypot(v.co.x - DART_X, v.co.z) < DART_NOZZLE[1] + 0.05):
            values.append(-9.0)    # the dark point and nozzle
        else:
            values.append(n.z)
    band_split(body, values, [(-99.0, m["dark"]), (-5.0, m["under"]), (-0.3, m["side"]), (0.45, m["body"]),
                              (0.9, m["stripe"])])
    k.smooth(body, 60)
    objects.append(body)
    # The band: a ring round the body near the nose, its crown glowing hotter.
    y0, y1, rb = DART_BAND
    band = k.lathe("band", [(y0, 0.0), (y0, rb - 0.15), (y0 + 0.15, rb), (y1 - 0.15, rb), (y1, rb - 0.15), (y1, 0.0)],
                   None, segments=24, axis_x=DART_X)
    band_split(band, [n.z for n in vertex_normals(band)], [(-99.0, band_side), (0.55, band_crown)])
    k.smooth(band, 50)
    objects.append(band)
    # The fins: either side flat (the sprite's), above and below upright and smaller.
    for i, plan in enumerate(FINS):
        for side in (-1, 1):
            objects.append(fin(f"fin{i}{'lr'[side > 0]}", [(side * x, y) for x, y in plan], DART_X, m["fin"],
                               m["fin_edge"]))
        for up in (-1, 1):  # (their rims light: from above, the light line down the body's middle)
            f = fin(f"fin{i}{'du'[up > 0]}", [(x * FIN_UPRIGHT, y) for x, y in plan], 0.0, m["fin"], m["stripe"])
            # turned upright about the axis (+x out to +z above, -z below)
            f.data.transform(Matrix.Translation((DART_X, 0, 0)) @ Matrix.Rotation(math.radians(-90 * up), 4, "Y"))
            objects.append(f)
    mk.transform(objects, HALF_TURN)  # nose up the screen, for yaw=velocity
    return objects


def dart_frames(frame):
    # (turned back half round, as the game shows it falling: yaw 180)
    return lambda: [(frame, turn(180), f"D {frame}")]


# --- D 191: the falling ice spike -------------------------------------------------------------------------------------

# The crystal: its axis (x, z), the half-width to its side corners and its half-height (a six-sided section, corners at
# the sides), from its point (y0) up to the break (y1): where the point's taper begins; the splinters: (x, from y, to y,
# radius, lean (dx over their length)).
ICE_X, ICE_Z = -0.5, 0.0
ICE_HALF, ICE_HEIGHT = 3.55, 2.5
ICE_Y = (-14.0, 8.9)
ICE_TAPER = -10.9
ICE_RINGS = 34
SPLINTERS = [(-2.45, 7.6, 14.0, 0.95, -0.4), (1.45, 7.6, 13.0, 0.85, 0.35), (-0.15, 7.9, 11.0, 0.9, 0.1)]
SPLINTER_RISE = 0.6   # how far their tips rise towards the camera
# The paint: a value per vertex from the facet (its normal's z: the top face, the slanted faces, the lower ones; the
# sun's side lighter) and along y (whitest in the lower middle, darker into the point, streaked above), in bands of
# ramp 3 (lowest value, palette index, emission strength).
ICE_BANDS = [(-99.0, 0x3a, 0.04), (10.4, 0x3b, 0.06), (11.2, 0x3c, 0.1), (12.0, 0x3d, 0.14), (12.8, 0x3e, 0.2),
             (13.7, 0x3f, 0.26)]
ICE_STREAKS = [(-0.6, 0.5, 9.0, 0.45, 1.7), (0.7, 2.0, 8.5, 0.35, 1.3), (-1.7, -3.0, 4.0, 0.3, 0.8)]
# The upper part cloudier in its middle (the sprite's 0x3b-0x3d there, its edges light): how much darker, from where
# to where along y.
ICE_CLOUD = (1.2, 0.5, 5.5)
# The crystal is not cut true: each of its six edges moved out or in by up to ICE_ROUGH (a share of the half-width;
# from a seeded generator, the same every run), the break's corners raised or lowered (pixels).
ICE_ROUGH, ICE_BREAK, ICE_SEED = 0.07, (0.9, -0.3, 0.5, -0.6, 0.2, 0.7), 191


def ice_value(x, y, n):
    up = n.z
    value = 9.6 + 3.6 * smoothstep(-0.2, 0.95, up)
    value += 0.7 * smoothstep(0.0, 0.6, -n.x) * smoothstep(0.1, 0.5, up)   # the sun's side (the left) lighter
    value += 1.0 * smoothstep(4.5, -1.0, y) * smoothstep(-12.5, -8.0, y)  # whitest in the lower middle
    value -= 1.4 * smoothstep(-10.5, -13.8, y)                             # darker into the point
    value -= ICE_CLOUD[0] * smoothstep(ICE_CLOUD[1], ICE_CLOUD[2], y) * smoothstep(0.75, 0.95, up) * \
        math.exp(-((x - ICE_X) / 1.4) ** 2)                                # the cloudy upper middle
    for sx, sy0, sy1, w, depth in ICE_STREAKS:                             # streaks in the upper part
        if sy0 < y < sy1:
            value -= (depth * math.exp(-((x - sx) / w) ** 2) * smoothstep(sy0, sy0 + 1.0, y) *
                      smoothstep(sy1, sy1 - 1.0, y))
    return value


def ice_spike(name):
    mats = [(lowest, lit(f"ice_{index:02x}", index, glow, roughness=0.12)) for lowest, index, glow in ICE_BANDS]
    y0, y1 = ICE_Y
    ys = [y0 + (y1 - y0) * i / ICE_RINGS for i in range(1, ICE_RINGS + 1)]
    ys = sorted(set(ys) | {y0 + d for d in (0.15, 0.45)})
    rough = random.Random(ICE_SEED)
    edges = [1 + ICE_ROUGH * (2 * rough.random() - 1) for _ in range(6)]
    rings = []
    for y in ys:
        f = 1.0 if y >= ICE_TAPER else max(0.03, ((y - y0) / (ICE_TAPER - y0)) ** 0.85)
        ring = facet_ring(y, ICE_HALF * f, ICE_HEIGHT * f, x=ICE_X, z=ICE_Z, sides=6, start=0.0)
        for p, out in zip(ring, edges):
            p.x = ICE_X + (p.x - ICE_X) * out
            p.z = ICE_Z + (p.z - ICE_Z) * out
        rings.append(ring)
    # The break: the top ring raised on the left, lower on the right, each corner on its own (an uneven fracture).
    top = rings[-1]
    for p, lift in zip(top, ICE_BREAK):
        p.y += 0.55 * (ICE_X - p.x) / ICE_HALF + 0.25 * (p.z / ICE_HEIGHT) + 0.5 * lift
    body = k.loft(name, rings, None, start_point=(ICE_X, y0, ICE_Z), end_point=(ICE_X - 0.3, y1 + 0.35, ICE_Z + 0.4))
    objects = [body]
    for i, (sx, sy0, sy1, r, lean) in enumerate(SPLINTERS):
        count = 8
        srings = []
        for j in range(count):
            u = j / (count - 1)
            y = sy0 + (sy1 - sy0 - 0.9) * u
            srings.append(facet_ring(y, r * (1 - 0.25 * u), r * 0.8 * (1 - 0.25 * u), x=sx + lean * u,
                                     z=ICE_Z + 0.4 + SPLINTER_RISE * u, sides=6, start=30.0 * i))
        splinter = k.loft(f"splinter{i}", srings, None, start_point=(sx, sy0, ICE_Z + 0.4),
                          end_point=(sx + lean, sy1, ICE_Z + 0.4 + SPLINTER_RISE))
        objects.append(splinter)
    for obj in objects:
        values = [ice_value(v.co.x, v.co.y, n) for v, n in zip(obj.data.vertices, vertex_normals(obj))]
        band_split(obj, values, mats)
        flat_shade(obj, 22)
    return objects


# --- Build ------------------------------------------------------------------------------------------------------------

MODELS = [
    # name, sheet, 2x2, make, frames for the check, moved to the frames' middles
    ("steel_needle", "S", False, steel_needle, steel_frames, True),
    ("twin_pellets", "D", False, twin_pellets, pellet_frames, False),
    ("white_dart", "D", False, lambda name: white_dart(name, 171), dart_frames(171), False),
    ("white_dart_190", "D", False, lambda name: white_dart(name, 190), dart_frames(190), False),
    ("white_dart_209", "D", False, lambda name: white_dart(name, 209), dart_frames(209), False),
    ("ice_spike", "D", True, ice_spike, lambda: [(191, turn(0), "D 191")], False),
]


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sheet, large, make, frames, move in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        objects = make(name)
        triangulate(objects)
        bpy.context.view_layer.update()
        if "check" in options:
            check_frames(objects, os.path.join(options["check"], f"enemy_{sheet}.png"), frames(), move_to_frame=move,
                         large=large)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, objects, os.path.join(mk.outdir(options), name + ".glb"))
        if "preview" in options:
            size = (24, 28) if large else (12, 14)
            mk.preview(options["preview"] + name, objects, size=size, scale=16 if large else 32,
                       distance=0.75 if large else 0.42)


if __name__ == "__main__":
    build()
