"""The tracked carrier of the asteroid levels (sheet S sprites 165 and 167 above 203 and 205, 2x2 each: one 48 x 56
picture; ground layer; ASTEROID2 (its boss) and AST. CITY, enemies 546-549 of episodes 1-3, GREY MOON and VAULT,
enemies 1573-1576 of episode 6), polished (2026-10-21; it replaces wave3_u_carrier.py's carrier_whole(), slabs and
rounded boxes over two belts). The missile launcher and the grey robot the levels set on its ball mount are
polish_carrier_turrets.py's; it takes MOUNT, BALL_C, BALL_R and the light from here.

Where the levels put it: event 12 ("4-part enemy") puts 546 (S 203) at (x, y), 547 (205) 24 pixels to its right, 548
(165) 28 pixels up the screen and 549 (167) both, nose down the screen; ASTEROID2 once (t 7482, the level's boss: its
four pieces and the launcher share link 45 and the boss bar), AST. CITY twelve times (t 412 ... 6824), episode 6's GREY
MOON (its mid-boss) and VAULT (its boss) once each: they take ASTEROID2's boss block, which keeps link 45 only, so the
carrier comes there bare, as in two of AST. CITY's twelve (t 1308, 4388). Each piece is an enemy of its own (armour 80):
shot away it leaves the others standing. At half armour all four (and a launcher on link 45) turn to their damaged
look (dgr 6, dani -6, dlevel 40: S 169 207 / 245 283, the ball burnt black, the treads broken); this script builds
those too (track_carrier_*_damaged, frame models). Their frames: the top pieces 165 165 241 241 ... (241 and 243 are
165's and 167's pixels with the engine grilles' slats one row on), the bottom ones 203 203 279 279 ... (279 and 281
with the tread bars one row on: the treads roll): no other enemy, launched ones included, shows S 241, 243, 279, 281,
169, 207, 245 or 283, so they get frame models. None of the sprites is another sprite's pixels mirrored, turned or in
other ramps (twins3.py: only their own frames come near).

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 56 picture; its axis between columns 23
and 24): two broad tracks, columns 3-18 and 30-45, their dark treads showing through windows in grey frames (rows
33-44) and bare round their front wheels (rows 45-55), the frames' skirts curving down in front (rows 45-52); over
their back halves the hull: at its back two engine decks, dark grilles of two lit slats (columns 6-15 and 33-42, rows
9-13); between them two grey posts (columns 16-21 and 28-32, rows 8-16) flanking a red block (columns 22-27, rows
9-13); a grey band across the hull (rows 14-16); in the middle the big grey ball of the mount (columns 19-30 of rows
13-26, lit at its upper left), held between two red plates (columns 10-18 and 31-38, rows 17-21) on beams across the
hull, red side armour outside them (columns 3-8 and 40-45, rows 18-28), cut away diagonally by the fenders; the grey
fenders over the tracks' fronts (rows 22-32), an inner rib and groove along each, a lit outer rim along the diagonal;
round the ball's foot a collar in a deck (rows 22-29), its front lip lit (rows 28-29); between the tracks a red glacis
plate (columns 19-29 of rows 31-44): its top lit (rows 33-35), its front sloping down (the dark triangle at its lower
left is the left track's shadow, which the game casts itself).

Built as such a vehicle for the game's camera, 20 degrees from straight down from the bottom of the screen, which
shows a point at height z about 0.36 z pixels further up the screen than its place on the ground: each part is laid
out where the sprites draw it and moved down the screen by what the camera shows its top further up (S(z)), its walls
kept upright, so that the camera sees the hull's tops where the sprites (and the hitboxes) are, and their fronts below
them as the sprites draw them. The parts are CAD solids (polish_machine_kit: prisms, wedges, exact booleans, bevels;
profiled(): a plan cut to a side and a cross profile): the tracks belts round two wheels with tread links all round
them (two pads each, every PITCH of 2 pixels, each pad worn a little its own way; the roll frames one pixel on)
between skirts whose fronts slope down; the hull a deck over them, its back corners chamfered, the grilles' recesses
cut into it after its bevel, their slats laid in; the posts (their tops falling to the back), the red block, the plates
on their beams and the side armour blocks (their tops sloping down outward) on it; the fenders blocks falling to a
rounded front and to the outside, a groove cut along each and a rib laid inside it; the glacis a profile along x,
sheared for the camera (its sides stay upright); the ball a sphere of even triangles in a collar, painted in bands
along smooth contours of how it faces the light (polish_orb_red.band_split), its glint a little emissive (the camera
sees a grey ball dark). Painted by how their faces meet the game's light (from the upper left and above): the greys
0x02 (the grilles' depths, the belts), 0x05 (shaded sides), 0x06 (the deck's and fenders' tops, the links), 0x08 (the
posts' tops, lit edges), 0x0a and 0x0c (lit rims); the ball 0x09, 0x0b, 0x0d and its glint 0x0f (emission 0.25); the
reds 0xa2 (deep), 0x42, 0x45 (tops) and 0x48 (lit). The damaged look keeps every part and lays soot over it where the
damaged sprites draw it darker (SOOT: the parts cut along the camera's pixel lines, soot 0x03, 0x02, 0x01 by how much
darker, along smooth contours, merged back where nothing changed), the ball burnt black (0x02, 0x05, 0x08 by the
light), a fifth of the tread links knocked off and a quarter askew.

The whole is triangulated and cut along the sprites' edges (x = 0, y = 0; this script's cut(): the caps given their
material as soon as they are made and shaded as tops, so a piece shot away shows its neighbour's inside lit as its
top), each piece moved so that its sprite's centre is its origin, every mesh triangulated (the same output with and
without --check) and its parts joined into one mesh (polish_deli_boss.join). Drawn at their origins (origin), on the
ground layer 4 pixels up: height=-4 on the sprite lines sets the carrier on the terrain.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0). The whole's
origin is the corner where the four sprites meet (pixel 24, 28 of the picture): E(c, r) is the picture's pixel corner
(c, r), (c - 24, 28 - r). The pieces' centres: 165 (-12, 14), 167 (12, 14), 203 (-12, -14), 205 (12, -14). The mount's
ball: BALL_C, its top MOUNT (in the whole's coordinates); the launcher's and the robot's sprites are centred 10 pixels
up the screen from the whole's origin, at x 0.

models.cfg: the model lines of track_carrier_tl / _tr / _bl / _br stay (origin); new: model track_carrier_tl_241,
track_carrier_tr_243, track_carrier_bl_279, track_carrier_br_281, track_carrier_tl_damaged, track_carrier_tr_damaged,
track_carrier_bl_damaged, track_carrier_br_damaged ... origin; the four sprite lines get height=-4; frame s 241
track_carrier_tl_241, frame s 243 track_carrier_tr_243, frame s 279 track_carrier_bl_279, frame s 281
track_carrier_br_281, frame s 169 track_carrier_tl_damaged, frame s 207 track_carrier_tr_damaged, frame s 245
track_carrier_bl_damaged, frame s 283 track_carrier_br_damaged.

Replaces wave3_u_carrier.py's carrier: its docstring bullet, ORIGIN, AX, px(), edge(), py(), row_edge(), mats()'s use
for the carrier, slab(), track(), _yz_to_xyz(), carrier_whole() with its @u.whole("carrier") registration,
carrier_piece() and the u.model("track_carrier_...") loop, loaded_whole() (the launcher and the robot are
polish_carrier_turrets.py's: with them wave3_u_carrier.py has nothing left to build and can be deleted, see that
script's docstring).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's and each piece's
silhouette against the sprites' pixels in enemy_S.png, from straight above and as the game's camera sees it),
--preview <prefix> (the whole's views; with --pieces 1 each piece's too), --only <model,...>, --looks
<rest,roll,damaged> (default all), --whole <prefix> (the uncut wholes as <prefix><look>.glb), --stats 1.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_orb_red import band_split, icosphere  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

TILT = math.tan(math.radians(20.0))   # how far up the screen the game's camera shows a point, per pixel of height
AX = 0.5                              # the carrier's axis (between the picture's columns 23 and 24)
LIGHT = Vector((-0.5, 0.5, 0.78)).normalized()   # towards the game's sun: from the upper left and above
CAMERA = Vector((0.0, -math.sin(math.radians(20.0)), math.cos(math.radians(20.0))))   # towards the game's camera

# The pieces: name, box (x0, x1, y0, y1) in the whole's coordinates; the sprites of each look.
PIECES = [("tl", (-24.0, 0.0, 0.0, 28.0)), ("tr", (0.0, 24.0, 0.0, 28.0)),
          ("bl", (-24.0, 0.0, -28.0, 0.0)), ("br", (0.0, 24.0, -28.0, 0.0))]
SPRITES = {"rest": {"tl": 165, "tr": 167, "bl": 203, "br": 205},
           "roll": {"tl": 241, "tr": 243, "bl": 279, "br": 281},
           "damaged": {"tl": 169, "tr": 207, "bl": 245, "br": 283}}
CORNER = {"tl": (0, 0), "tr": (24, 0), "bl": (0, 28), "br": (24, 28)}


def E(c, r):
    """The picture's pixel corner (column c, row r) in the whole's coordinates, as the sprites draw it."""
    return (c - 24.0, 28.0 - r)


def S(z):
    """How far up the screen the game's camera shows a point at height z, against its place on the ground."""
    return z * TILT


def shift(objs, z):
    """Moves parts down the screen by S(z): the camera then sees their tops at height z where the sprites draw them."""
    for obj in objs if isinstance(objs, (list, tuple)) else [objs]:
        obj.data.transform(Matrix.Translation((0.0, -S(z), 0.0)))
    return objs


def mirror(points):
    """A plan's mirror image about the axis (its order reversed, so that it stays counter-clockwise)."""
    return [(2 * AX - x, y) for x, y in reversed(points)]


# --- The layout (as the sprites draw it, before the camera's shift) -------------------------------------------------

# The tracks: the left one's outer and inner edges (x), the skirts' width; the right one is its mirror image.
TRACK_X = (-21.0, -5.0)
SKIRT = 2.7
# The belts (physical: y of the back and front wheels, their radius), the tread links' pitch and size (along the
# belt, how high) and the gap between a link's two pads.
WHEEL_BACK, WHEEL_FRONT, WHEEL_R = 13.4, -25.0, 3.3
PITCH = 2.0
LINK = (1.25, 0.75)
PAD_GAP = 0.8
# The skirts' side profile (y, z), physical: along the belt, their tops 7.4 high, their fronts sloping down.
SKIRT_PROFILE = [(14.2, 0.5), (14.2, 7.4), (-19.4, 7.4), (-22.8, 5.9), (-25.4, 3.6), (-26.4, 1.6), (-26.0, 0.5)]

# The hull: a deck over the tracks (its plan, its top, its bottom), its back corners chamfered.
HULL_PLAN = [(-20.75, 16.2), (-20.75, -2.0), (21.75, -2.0), (21.75, 16.2), (19.0, 19.1), (-18.0, 19.1)]
HULL_TOP, HULL_BOTTOM = 8.4, 4.2
CORE = (-4.7, 5.7, 17.0, -1.6, 1.0)   # the box between the tracks under the deck (x0, x1, y0, y1, z0)
# The engine grilles (left; x0, x1, y0, y1 as drawn), their depth, the slats (rows as drawn, per look).
GRILLE = (-18.0, -8.2, 18.65, 14.35)
GRILLE_DEPTH = 1.5
SLATS = {"rest": (10.0, 12.0), "roll": (9.15, 11.0, 13.0)}
# The posts (left: x0, x1, y0, y1, top), the red block between them (x0, x1, y0, y1, top).
POST = (-8.0, -2.15, 20.0, 11.4, 10.9)
RED_BLOCK = (-2.15, 3.15, 19.1, 13.8, 10.2)
# The ball of the mount: where the sprites draw its middle (x, y), its height there and radii.
BALL_DRAWN = (AX, 8.1)
BALL_Z = 9.8
BALL_R = (6.0, 6.0, 5.8)
BALL_C = Vector((BALL_DRAWN[0], BALL_DRAWN[1] - S(BALL_Z), BALL_Z))   # (physical)
MOUNT = Vector((BALL_C.x, BALL_C.y, BALL_C.z + BALL_R[2]))           # the ball's top, where the turrets sit
COLLAR = [(5.2, 7.4), (6.9, 7.4), (7.3, 8.25), (7.0, 9.15), (6.2, 9.6), (5.2, 9.55)]   # (radius, z)
# The plates on their beams (left: x0, x1, y0, y1 as drawn, bottom, top).
PLATE = (-14.2, -5.0, 11.15, 6.35, 8.2, 11.4)
# The side armour (left; its plan as drawn, its top at the inner and the outer edge, its bottom).
ARMOUR_PLAN = [(-21.3, 10.7), (-21.3, -0.6), (-19.4, 2.25), (-16.6, 6.45), (-14.9, 6.45), (-14.9, 10.7)]
ARMOUR_Z = (10.4, 8.6, 6.8)
# The fenders (left; plan as drawn; their side profile (y, z) and cross profile (x, z), their bottom), the groove
# (x, half width, depth) and the rib inside it (x0, x1, how high over the fender).
FENDER_PLAN = [(-21.3, -0.6), (-21.3, -4.7), (-5.0, -4.7), (-5.0, 6.45), (-16.6, 6.45), (-19.4, 2.25)]
FENDER_SIDE = [(8.0, 0.0), (8.0, 9.5), (6.45, 9.5), (-2.6, 8.9), (-3.9, 8.45), (-4.7, 7.5), (-4.95, 6.6),
               (-6.0, 0.0)]
FENDER_CROSS = [(-4.0, 0.0), (-4.0, 10.1), (-6.0, 10.05), (-9.0, 9.9), (-12.5, 9.65), (-15.5, 9.3), (-18.0, 8.8),
                (-19.8, 8.2), (-21.0, 7.4), (-21.6, 6.4), (-22.5, 0.0)]
FENDER_BOTTOM = 6.6
FENDER_SHIFT = 9.0
GROOVE = (-9.1, 0.45, 0.9)
RIB = (-8.6, -5.0, 0.55)
# The glacis: its side profile (y, z as drawn) along x from x0 to x1.
GLACIS_X = (-4.85, 5.85)
GLACIS = [(-1.6, 1.0), (-1.6, 6.3), (-8.2, 6.3), (-16.3, 1.5), (-16.75, 0.5), (-16.3, 0.0), (-1.6, 0.0)]

# Bands of how a face meets the light (normal . LIGHT): [(lowest, material key)].
GREY_BANDS = [(-9.0, "shade"), (0.45, "steel"), (0.84, "lit"), (0.965, "bright")]
DECK_BANDS = [(-9.0, "shade"), (0.45, "mid"), (0.84, "lit"), (0.965, "bright")]
TREAD_BANDS = [(-9.0, "shade"), (0.82, "mid"), (0.93, "steel")]
POST_BANDS = [(-9.0, "shade"), (0.45, "steel"), (0.8, "lit"), (0.95, "bright")]
RED_BANDS = [(-9.0, "red_dark"), (0.5, "red"), (0.9, "red_lit")]


# --- Materials -----------------------------------------------------------------------------------------------------

def materials(prefix="tc"):
    pal = k.level_palette()

    def mat(name, index, metallic, roughness, glow=0.0, glow_index=None):
        emission = pal[glow_index if glow_index is not None else index] if glow > 0 else None
        return k.material(f"{prefix}_{name}", palette=index, metallic=metallic, roughness=roughness,
                          emission=emission, emission_strength=glow)
    return {
        "deep": mat("deep", 0x02, 0.3, 0.6), "shade": mat("shade", 0x05, 0.35, 0.5), "mid": mat("mid", 0x06, 0.35, 0.48),
        "steel": mat("steel", 0x08, 0.35, 0.45), "lit": mat("lit", 0x0a, 0.35, 0.42),
        "bright": mat("bright", 0x0c, 0.35, 0.4),
        "ball0": mat("ball", 0x09, 0.3, 0.32), "ball1": mat("ball_lit", 0x0b, 0.3, 0.3),
        "ball2": mat("ball_bright", 0x0d, 0.3, 0.28), "glint": mat("ball_glint", 0x0f, 0.2, 0.25, 0.25),
        "red_deep": mat("maroon", 0xa2, 0.3, 0.5), "red_dark": mat("red_dark", 0x42, 0.3, 0.45),
        "red": mat("red", 0x45, 0.3, 0.42), "red_lit": mat("red_lit", 0x48, 0.3, 0.4),
    }


def light_paint(obj, m, bands, override=None):
    """Gives each face the material of its band of normal . LIGHT (override(centre, normal) may pick another)."""
    def pick(c, n):
        if override is not None:
            key = override(c, n)
            if key is not None:
                return m[key]
        v = n.dot(LIGHT)
        key = bands[0][1]
        for low, kk in bands:
            if v >= low:
                key = kk
        return m[key]
    return mk.paint(obj, pick)


def profiled(name, plan, side_profile, cross_profile, bottom, mat):
    """A block over a plan (x, y), cut to a side profile (y, z, along x) and a cross profile (x, z, along y), standing
    on bottom: the intersection of the three prisms (exact booleans)."""
    xs, ys = [p[0] for p in plan], [p[1] for p in plan]
    body = mk.prism(name, plan, bottom, 40.0, mat)
    if side_profile is not None:
        cutter = mk.prism(name + "_side", side_profile, min(xs) - 2.0, max(xs) + 2.0, mat, axis="x")
        mk.boolean(body, cutter, "INTERSECT")
    if cross_profile is not None:
        cutter = mk.prism(name + "_cross", cross_profile, min(ys) - 2.0, max(ys) + 2.0, mat, axis="y")
        mk.boolean(body, cutter, "INTERSECT")
    mk.cleanup(body)
    return body


# --- The tracks ----------------------------------------------------------------------------------------------------

def belt_path(step):
    """Points round the belt (y, z, the outward normal's y and z), every step along it, starting at the top of the
    back wheel and running forward along the top, round the front wheel, back along the bottom."""
    r = WHEEL_R
    length_top = WHEEL_BACK - WHEEL_FRONT
    arc = math.pi * r
    total = 2 * length_top + 2 * arc
    pts = []
    s = 0.0
    while s < total - 1e-6:
        if s < length_top:
            pts.append((WHEEL_BACK - s, 2 * r, 0.0, 1.0))
        elif s < length_top + arc:
            a = math.pi / 2 + (s - length_top) / r   # round the front wheel, from its top down
            pts.append((WHEEL_FRONT + r * math.cos(a), r + r * math.sin(a), math.cos(a), math.sin(a)))
        elif s < 2 * length_top + arc:
            pts.append((WHEEL_FRONT + (s - length_top - arc), 0.0, 0.0, -1.0))
        else:
            a = -math.pi / 2 + (s - 2 * length_top - arc) / r   # round the back wheel, from its bottom up
            pts.append((WHEEL_BACK + r * math.cos(a), r + r * math.sin(a), math.cos(a), math.sin(a)))
        s += step
    return pts


def track_parts(m, side, look, rng):
    """A track (side -1 the left, 1 the right): the belt round its wheels, tread links all round it, each two pads
    (look "roll": one pixel on; "damaged": some knocked off, others askew), the skirts either side."""
    x0, x1 = TRACK_X if side < 0 else (2 * AX - TRACK_X[1], 2 * AX - TRACK_X[0])
    bx0, bx1 = x0 + SKIRT - 0.05, x1 - SKIRT + 0.05
    mid = (bx0 + bx1) / 2
    parts = []
    # The belt: the stadium round both wheels, its outline in (y, z), extruded across.
    outline = []
    for i in range(13):
        a = math.pi / 2 + math.pi * i / 12
        outline.append((WHEEL_FRONT + WHEEL_R * math.cos(a), WHEEL_R + WHEEL_R * math.sin(a)))
    for i in range(13):
        a = -math.pi / 2 + math.pi * i / 12
        outline.append((WHEEL_BACK + WHEEL_R * math.cos(a), WHEEL_R + WHEEL_R * math.sin(a)))
    belt = mk.prism(f"belt{side}", outline, bx0 + 0.3, bx1 - 0.3, m["deep"], axis="x")
    k.smooth(belt, 40)
    parts.append(belt)
    # The tread links: two rounded pads across the belt, every PITCH along it (where they can be seen).
    phase = PITCH / 2 if look == "roll" else 0.0
    thick, high = LINK
    step = 0.05
    path = belt_path(step)
    s = phase
    i = 0
    while s < len(path) * step:
        y, z, ny, nz = path[int(s / step)]
        s += PITCH
        i += 1
        if nz < -0.5 or y > -5.5:              # the bottom run, and all under the hull and the fenders: never seen
            continue
        tilt = 0.0
        if look == "damaged":
            roll = rng.random()
            if roll < 0.2:
                continue                       # knocked off
            if roll < 0.45:
                tilt = rng.uniform(-16.0, 16.0)
        for j, (p0, p1) in enumerate(((bx0, mid - PAD_GAP / 2), (mid + PAD_GAP / 2, bx1))):
            # Each pad a little worn its own way (its ends and thickness), so that the links don't read as a ladder.
            p0, p1 = p0 + rng.uniform(0.0, 0.25), p1 - rng.uniform(0.0, 0.25)
            t = thick * rng.uniform(0.85, 1.05)
            pad = mk.box(f"tread{side}_{i}_{j}", p0, p1, -t / 2, t / 2, -0.25, high * rng.uniform(0.85, 1.0),
                         m["steel"])
            mk.bevel(pad, 0.3, 2, 35)
            angle = math.atan2(-ny, nz)
            pad.data.transform(Matrix.Translation((0.0, y, z)) @ Matrix.Rotation(angle, 4, "X") @
                               Matrix.Translation(((p0 + p1) / 2, 0, 0)) @ Matrix.Rotation(math.radians(tilt), 4, "Y")
                               @ Matrix.Translation((-(p0 + p1) / 2, 0, 0)))
            light_paint(pad, m, TREAD_BANDS)
            mk.shade(pad, 35)
            parts.append(pad)
    # The skirts either side of the belt: plates along it, their fronts sloping down round the front wheel.
    for j, (sx0, sx1) in enumerate(((x0, x0 + SKIRT), (x1 - SKIRT, x1))):
        skirt = mk.prism(f"skirt{side}_{j}", SKIRT_PROFILE, sx0, sx1, m["steel"], axis="x")
        mk.bevel(skirt, 0.55, 3, 35)

        def pick(c, n):
            if n.z > 0.9:
                return "steel"
            if n.z > 0.25 and n.y < -0.25:     # the rounded corner at the top of the front: catching the light
                return "lit"
            if n.y < -0.3:
                return "shade"
            return None
        light_paint(skirt, m, GREY_BANDS, pick)
        mk.shade(skirt, 35)
        parts.append(skirt)
    return parts


# --- The hull ------------------------------------------------------------------------------------------------------

def grille_box(side):
    x0, x1, y0, y1 = GRILLE
    if side > 0:
        x0, x1 = 2 * AX - x1, 2 * AX - x0
    return x0, x1, y0, y1


def hull_parts(m, look):
    """The deck over the tracks, the box under it between them, the grilles' recesses in it and their slats."""
    deck = mk.prism("hull", HULL_PLAN, HULL_BOTTOM, HULL_TOP, m["steel"])
    x0, x1, y0, y1, z0 = CORE
    core = mk.box("hull_core", x0, x1, y1, y0, z0, HULL_TOP - 0.5, m["shade"])
    mk.boolean(deck, core, "UNION")
    mk.cleanup(deck)
    mk.bevel(deck, 0.7, 3, 35)
    for side in (-1, 1):   # the grilles' recesses, cut after the deck's bevel, their own edges rounded less
        gx0, gx1, gy0, gy1 = grille_box(side)
        cutter = mk.box(f"grille_cut{side}", gx0, gx1, gy1, gy0, HULL_TOP - GRILLE_DEPTH, HULL_TOP + 2.0, m["deep"])
        mk.boolean(deck, cutter, "DIFFERENCE")
    mk.cleanup(deck)
    mk.bevel(deck, 0.25, 2, 35)

    def pick(c, n):
        for side in (-1, 1):
            gx0, gx1, gy0, gy1 = grille_box(side)
            if gx0 - 0.1 < c.x < gx1 + 0.1 and gy1 - 0.1 < c.y < gy0 + 0.1 and c.z < HULL_TOP - 0.2:
                return "deep"
        if abs(n.x) > 0.8 and -0.6 < c.y < 10.6:   # the sides under the side armour
            return "red_deep"
        return None
    light_paint(deck, m, DECK_BANDS, pick)
    mk.shade(deck, 35)
    parts = [deck]
    # The slats across the grilles: round bars, lit along their tops.
    for side in (-1, 1):
        gx0, gx1, gy0, gy1 = grille_box(side)
        for i, row in enumerate(SLATS["roll" if look == "roll" else "rest"]):
            y = 28.0 - (row + 0.5)
            y = min(max(y, gy1 + 0.5), gy0 - 0.5)
            slat = mk.tube(f"slat{side}_{i}", [(gx0 + 0.15, y, HULL_TOP - 0.8), (gx1 - 0.15, y, HULL_TOP - 0.8)],
                           0.52, m["steel"], segments=12)
            light_paint(slat, m, [(-9.0, "shade"), (0.4, "steel"), (0.85, "lit")])
            k.smooth(slat, 60)
            parts.append(slat)
    shift(parts, HULL_TOP)
    return parts


def block(name, x0, x1, y0, y1, z0, z1, mat, bevel):
    obj = mk.box(name, x0, x1, y1, y0, z0, z1, mat)
    mk.bevel(obj, bevel, 3, 35)
    return obj


def post_parts(m):
    """The two grey posts at the back, their tops falling to the back, and the red block between them."""
    parts = []
    x0, x1, y0, y1, top = POST
    for side in (-1, 1):
        a, b = (x0, x1) if side < 0 else (2 * AX - x1, 2 * AX - x0)
        post = profiled(f"post{side}", [(a, y1), (b, y1), (b, y0), (a, y0)],
                        [(y1 - 1.0, HULL_TOP - 1.0), (y1 - 1.0, top), (y0 - 2.6, top), (y0, top - 1.6),
                         (y0 + 1.0, HULL_TOP - 1.0)], None, HULL_TOP - 1.0, m["steel"])
        mk.bevel(post, 0.9, 3, 30)
        light_paint(post, m, POST_BANDS)
        mk.shade(post, 30)
        parts.append(shift(post, top))
    x0, x1, y0, y1, top = RED_BLOCK
    red = block("red_block", x0, x1, y0, y1, HULL_TOP - 1.0, top, m["red"], 0.8)
    light_paint(red, m, RED_BANDS, lambda c, n: "red_deep" if n.x < -0.6 else None)
    mk.shade(red, 35)
    parts.append(shift(red, top))
    return parts


def plate_parts(m):
    """The red plates on their beams either side of the ball, their edges rounded, lit at the front."""
    parts = []
    x0, x1, y0, y1, z0, z1 = PLATE
    for side in (-1, 1):
        a, b = (x0, x1) if side < 0 else (2 * AX - x1, 2 * AX - x0)
        plate = block(f"plate{side}", a, b, y0, y1, z0, z1, m["red"], 0.6)
        light_paint(plate, m, RED_BANDS, lambda c, n: "red_lit" if n.y < -0.7 else None)
        mk.shade(plate, 35)
        parts.append(shift(plate, z1))
    return parts


def armour_parts(m):
    """The red side armour: blocks on the deck's sides, their tops sloping down outward, their edges rounded."""
    parts = []
    inner, outer, bottom = ARMOUR_Z
    for side in (-1, 1):
        plan = ARMOUR_PLAN if side < 0 else mirror(ARMOUR_PLAN)
        xi = -14.9 if side < 0 else 2 * AX + 14.9
        xo = -21.3 if side < 0 else 2 * AX + 21.3
        cross = [(xi + 2.0 * (xi - xo) / abs(xi - xo), 0.0), (xi + 2.0 * (xi - xo) / abs(xi - xo), inner),
                 (xi, inner), (xo + 0.9 * (xi - xo) / abs(xi - xo), outer), (xo, outer - 1.1),
                 (xo - 0.5 * (xi - xo) / abs(xi - xo), 0.0)]
        body = profiled(f"armour{side}", plan, None, cross, bottom, m["red"])
        mk.bevel(body, 0.75, 3, 25)
        light_paint(body, m, RED_BANDS, lambda c, n: "red_deep" if n.z < 0.25 else None)
        mk.shade(body, 25)
        parts.append(shift(body, (inner + outer) / 2))
    return parts


def fender_parts(m):
    """The fenders over the tracks' fronts: blocks falling to a rounded front and to the outside, a groove cut along
    each, a rib laid inside it."""
    parts = []
    for side in (-1, 1):
        plan = FENDER_PLAN if side < 0 else mirror(FENDER_PLAN)
        cross = FENDER_CROSS if side < 0 else [(2 * AX - x, z) for x, z in FENDER_CROSS]
        body = profiled(f"fender{side}", plan, FENDER_SIDE, cross, FENDER_BOTTOM, m["steel"])
        gx = GROOVE[0] if side < 0 else 2 * AX - GROOVE[0]
        cutter = mk.box(f"groove{side}", gx - GROOVE[1], gx + GROOVE[1], -6.0, 5.6, 0.0, 20.0)
        top_z = mk.surface([body])
        for v in cutter.data.vertices:      # the groove's floor follows the top
            if v.co.z < 10.0:
                hit = top_z(v.co.x, min(v.co.y, 5.5) if v.co.y > -4.2 else -4.2)
                v.co.z = (hit[0].z if hit else 8.6) - GROOVE[2]
        mk.boolean(body, cutter, "DIFFERENCE")
        mk.cleanup(body)
        mk.bevel(body, 0.85, 3, 28)

        def pick(c, n, gx=gx):
            if abs(c.x - gx) < GROOVE[1] + 0.05 and n.z > 0.5 and c.z < 9.3:
                return "deep"
            return None
        light_paint(body, m, DECK_BANDS, pick)
        mk.shade(body, 28)
        parts.append(body)
        rx0, rx1 = (RIB[0], RIB[1]) if side < 0 else (2 * AX - RIB[1], 2 * AX - RIB[0])
        rib = profiled(f"rib{side}", [(rx0, -4.0), (rx1, -4.0), (rx1, 6.0), (rx0, 6.0)],
                       [(y, z + RIB[2]) for y, z in FENDER_SIDE], None, FENDER_BOTTOM, m["steel"])
        mk.bevel(rib, 0.45, 2, 30)
        light_paint(rib, m, GREY_BANDS)
        mk.shade(rib, 30)
        parts.append(rib)
    shift(parts, FENDER_SHIFT)
    return parts


def glacis_parts(m):
    """The red glacis plate between the tracks: its profile along x, sheared for the camera (its sides upright)."""
    body = mk.prism("glacis", GLACIS, GLACIS_X[0], GLACIS_X[1], m["red"], axis="x")
    for v in body.data.vertices:
        v.co.y -= S(v.co.z)
    mk.bevel(body, 0.8, 3, 30)
    light_paint(body, m, RED_BANDS, lambda c, n: "red_dark" if abs(n.x) > 0.7 else None)
    mk.shade(body, 30)
    return [body]


# --- The ball and its collar ---------------------------------------------------------------------------------------

BALL_BANDS = [(-9.0, "ball0"), (0.4, "ball1"), (0.72, "ball2"), (0.93, "glint")]
BURNT_BANDS = [(-9.0, "deep"), (0.6, "shade"), (0.92, "steel")]


def ball_parts(m, look):
    """The mount's ball (even triangles, its lower part sunk in the collar left off) and the collar round its foot."""
    ball = icosphere("ball", tuple(BALL_C), BALL_R, subdivisions=4)
    bm = bmesh.new()
    bm.from_mesh(ball.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if max(v.co.z for v in f.verts) < HULL_TOP - 1.4], context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.to_mesh(ball.data)
    bm.free()
    glint = Vector((-0.42, 0.42, 0.8)).normalized()

    def value(co):
        rel = co - BALL_C
        n = Vector((rel.x / BALL_R[0] ** 2, rel.y / BALL_R[1] ** 2, rel.z / BALL_R[2] ** 2)).normalized()
        v = n.dot(LIGHT)
        if look != "damaged":
            v = max(v, 0.25 + 0.75 * max(0.0, n.dot(glint)) ** 6)
        return v
    values = [value(v.co) for v in ball.data.vertices]
    bands = BURNT_BANDS if look == "damaged" else BALL_BANDS
    band_split(ball, values, [(low, m[key]) for low, key in bands])
    k.smooth(ball, 80)
    parts = [ball]
    # The collar: a ring round the ball's foot on the deck.
    collar = mk.lathe("collar", COLLAR, (BALL_C.x, BALL_C.y), m["steel"], segments=48)
    light_paint(collar, m, GREY_BANDS)
    k.smooth(collar, 50)
    parts.append(collar)
    return parts


# --- The damaged look ----------------------------------------------------------------------------------------------

# How much darker the damaged sprites (S 169 207 / 245 283) draw each pixel of the 48 x 56 picture than the intact
# ones (165 167 / 203 205): their shade (index & 15) less, 0-9 ('.' see-through in both), by sootmap.py.
SOOT = """
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................0000000.....00000...............
......0000000000000000000000000000000000000.....
......0734556530000000000000000000024445530.....
....00000000000000000000000000000000000000000...
...0000012333310000000000000000000022333330000..
...0000000000001000000000000000001010000000000..
...0000000012121000000000222000133456544210000..
...0000000223100000000004666402667555553200000..
...0000014122321100000489986634576555511000000..
...0000130000000000006999986621000000000000000..
...0000000000000000046899866620000000000000000..
...0000000000000000267966488720000000000000000..
...0000000000000000278986467720000000000000000..
...0000000000000000025886446620000000000000000..
...0000000000000000004888646200000000122000000..
...0000000000000000025777650000110001233200000..
...0000000000110000002322000001222013325200000..
...0000000001221000000000000002351124313100000..
...0000003200120000000000000013533024314000000..
...0000044420121000022222001345330134204000000..
...0000444400121002565555524565411233044200000..
...0002442000110035777777763677531100044400000..
...0002520012210133544444441032200000003322000..
...0002330133210254000000000000001000002455400..
...0001321213320253000000000000000000000124520..
...0000100111122255000000000000000000000013510..
...0000001111112254000000000000000023222212100..
...0000001333222254000000000000000000000010000..
...0100000010210455000000000000000112112322000..
...1331134434332654000000000000000000000010000..
...2550013300000342000000000000000133233433000..
...2551145524430131000000000000010000103210000..
...4551200000100131000000000000120277665543000..
...2651377654540131000000000000130023332210000..
...0210122200100121000000000000231478888532000..
...0002478888430010000000000000130010000000000..
...0001233320000000000000000000023110110001000..
...0004211111110000...........0123333422210000..
...0024333433320000...........0130111000000000..
...0122000011100000...........0126223222100000..
...0027223333210000...........0220000000000000..
...0010000000000000...........0124222211111000..
...0015222222220000...........0010000000000000..
...0011000000000000...........0001233221111000..
...0003233222220000...........000000000000000...
...000000000000000...............0232000001.....
......1132000100.................0000000000.....
......0000000000................................
"""
SOOT_BANDS = [(1.1, "soot_light"), (2.3, "soot"), (4.0, "soot_dark")]


def soot_materials(m, prefix):
    m["soot_light"] = k.material(f"{prefix}_soot_light", palette=0x03, metallic=0.2, roughness=0.65)
    m["soot"] = k.material(f"{prefix}_soot", palette=0x02, metallic=0.15, roughness=0.72)
    m["soot_dark"] = k.material(f"{prefix}_soot_dark", palette=0x01, metallic=0.1, roughness=0.8)
    return m


def soot_grid(text):
    rows = [line for line in text.strip().splitlines()]
    return [[0.0 if ch == "." else float(ch) for ch in row] for row in rows]


def blurred(grid, passes=1):
    """The grid smoothed a little (a 3 x 3 average, edges kept), so that the soot's borders run as smooth curves."""
    h, w = len(grid), len(grid[0])
    for _ in range(passes):
        out = [[0.0] * w for _ in range(h)]
        for r in range(h):
            for c in range(w):
                total, count = 0.0, 0.0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < h and 0 <= cc < w:
                            weight = 2.0 if dr == 0 and dc == 0 else 1.0
                            total += grid[rr][cc] * weight
                            count += weight
                out[r][c] = total / count
        grid = out
    return grid


def sample(grid, c, r):
    """The grid's value at the picture point (c, r) (pixel corners: a pixel's middle is c + 0.5), bilinear."""
    h, w = len(grid), len(grid[0])
    x, y = c - 0.5, r - 0.5
    x0, y0 = int(math.floor(x)), int(math.floor(y))
    fx, fy = x - x0, y - y0

    def at(cc, rr):
        cc, rr = min(max(cc, 0), w - 1), min(max(rr, 0), h - 1)
        return grid[rr][cc]
    return ((at(x0, y0) * (1 - fx) + at(x0 + 1, y0) * fx) * (1 - fy) +
            (at(x0, y0 + 1) * (1 - fx) + at(x0 + 1, y0 + 1) * fx) * fy)


def seen_bisect(obj, box, step=1.0):
    """Cuts the faces along planes x = const and along the camera's lines of sight's planes y + S(z) = const, every
    step: the soot then follows the pixels where the camera sees them."""
    x0, x1, y0, y1 = box
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    n = Vector((0.0, 1.0, TILT)).normalized()
    for i in range(int(math.floor(x0 / step)), int(math.ceil(x1 / step)) + 1):
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                               plane_co=(i * step, 0.0, 0.0), plane_no=(1.0, 0.0, 0.0))
    for i in range(int(math.floor(y0 / step)), int(math.ceil(y1 / step)) + 1):
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                               plane_co=(0.0, i * step, 0.0), plane_no=tuple(n))
    bm.to_mesh(obj.data)
    bm.free()


def overpaint(obj, values, bands):
    """polish_orb_red.band_split, but the parts of faces under the lowest band keep their own material (bands: [(lowest
    value, material)], ascending): the soot laid over the paint along smooth contours."""
    mesh = obj.data
    co = [v.co.copy() for v in mesh.vertices]
    vals = list(values)
    cuts = {}

    def cut(a, b, t):
        key = (min(a, b), max(a, b), t)
        if key not in cuts:
            f = (t - vals[a]) / (vals[b] - vals[a])
            co.append(co[a].lerp(co[b], f))
            vals.append(t)
            cuts[key] = len(co) - 1
        return cuts[key]

    def clip(poly, t, above):
        out = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            ina, inb = (vals[a] >= t) == above, (vals[b] >= t) == above
            if ina:
                out.append(a)
            if ina != inb:
                out.append(cut(a, b, t))
        return out

    levels = [(-1e9, None)] + list(bands)
    faces, mats, smooth = [], [], []
    for poly in mesh.polygons:
        own = mesh.materials[poly.material_index]
        indices = list(poly.vertices)
        low, high = min(vals[i] for i in indices), max(vals[i] for i in indices)
        for b in range(len(levels)):
            lo = levels[b][0]
            hi = levels[b + 1][0] if b + 1 < len(levels) else 1e9
            if high < lo or low >= hi:
                continue
            piece = indices
            if b > 0 and low < lo:
                piece = clip(piece, lo, True)
            if b + 1 < len(levels) and high >= hi:
                piece = clip(piece, hi, False)
            if len(piece) >= 3:
                faces.append(piece)
                mats.append(levels[b][1] or own)
                smooth.append(poly.use_smooth)
    slots = []
    for mt in mats:
        if mt not in slots:
            slots.append(mt)
    new = bpy.data.meshes.new(mesh.name)
    new.from_pydata([tuple(c) for c in co], [], faces)
    for mt in slots:
        new.materials.append(mt)
    for poly, mt in zip(new.polygons, mats):
        poly.material_index = slots.index(mt)
    new.validate()
    obj.data = new
    bm = bmesh.new()
    bm.from_mesh(new)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    bm.to_mesh(new)
    bm.free()
    k.recalc_normals(obj)
    return obj


def soot(objects, grid, m, origin, size, skip=()):
    """Lays soot over the parts where the damaged sprites draw them darker: grid (rows of 0-9, the picture as the
    levels place the sprites, w x h = size) sampled where the camera sees each point (its picture column x - origin
    x, row origin y - (y + S(z)))."""
    w, h = size
    grid = blurred(grid, 1)
    ox, oy = origin
    for obj in objects:
        if obj.name.startswith(tuple(skip)):
            continue
        mk.apply(obj)
        values = [sample(grid, v.co.x - ox, oy - (v.co.y + S(v.co.z))) for v in obj.data.vertices]
        if max(values) < SOOT_BANDS[0][0] and len(obj.data.vertices) > 40:
            continue                           # nothing of it darker (a small part is sampled at its corners only)
        low, high = mk.bounds([obj])
        seen_bisect(obj, (low.x, high.x, low.y + S(low.z) - 1.0, high.y + S(high.z) + 1.0))
        values = [sample(grid, v.co.x - ox, oy - (v.co.y + S(v.co.z))) for v in obj.data.vertices]
        overpaint(obj, values, [(low_, m[key]) for low_, key in SOOT_BANDS])
        mk.cleanup(obj, merge=1e-4, dissolve=0.5)   # the grid merged back where it painted nothing new
        mk.shade(obj, 35)


def damage(whole, m):
    """The carrier's damaged look: soot laid over every part where S 169 207 / 245 283 draw it darker (the ball burnt
    already by BURNT_BANDS, the tread links knocked off and askew by track_parts)."""
    soot_materials(m, "tc")
    soot(whole, soot_grid(SOOT), m, (-24.0, 28.0), (48, 56), skip=("ball",))


# --- The whole -----------------------------------------------------------------------------------------------------

CAPS = {"belt": "deep", "tread": "shade", "skirt": "shade", "hull": "shade", "slat": "shade", "post": "shade",
        "red": "red_dark", "plate": "red_dark", "armour": "red_dark", "fender": "shade", "rib": "shade",
        "glacis": "red_dark", "ball": "ball0", "collar": "shade"}


def build_whole(look):
    m = materials()
    rng = random.Random(7)
    parts = []
    for side in (-1, 1):
        parts += track_parts(m, side, look, rng)
    parts += hull_parts(m, look)
    parts += post_parts(m)
    parts += plate_parts(m)
    parts += armour_parts(m)
    parts += fender_parts(m)
    parts += glacis_parts(m)
    parts += ball_parts(m, look)
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts, m


def cap_of(obj, m):
    for prefix in sorted(CAPS, key=len, reverse=True):
        if obj.name.startswith(prefix):
            return m[CAPS[prefix]]
    return m["shade"]


CAP_NORMAL = (0.0, 0.0, 1.0)


def cut(source, box_xy, cap_mat):
    """The part of an object inside a box (x0, x1, y0, y1), its cuts capped with cap_mat (given as soon as they are
    made, so that a cap a later plane cuts keeps it; shaded as tops), its normals the uncut object's (polish_coral_
    manta.cut). None if nothing of it is inside the box."""
    x0, x1, y0, y1 = box_xy
    corners = [source.matrix_world @ Vector(c) for c in source.bound_box]
    if (max(c.x for c in corners) <= x0 or min(c.x for c in corners) >= x1 or
            max(c.y for c in corners) <= y0 or min(c.y for c in corners) >= y1):
        return None
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    cap_index = mk.slot_of(obj, cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    planes = (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0)))
    for co, no in planes:
        if not bm.faces:
            break
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                        plane_no=no, clear_outer=True)
        edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            if filled["faces"]:
                for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:
                    f.normal_update()
                    if f.normal.dot(Vector(no)) < 0:
                        f.normal_flip()
                    f.material_index = cap_index
                    f.smooth = False
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    on_cut = {f for f in bm.faces if f.material_index == cap_index and not f.smooth}
    bm.normal_update()
    bm.faces.index_update()
    cap_ids = {f.index for f in on_cut}
    bm.to_mesh(obj.data)
    bm.free()
    shading = mk.NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.index not in cap_ids:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else CAP_NORMAL))
    mesh.normals_split_custom_set(normals)
    return obj


# --- Checks --------------------------------------------------------------------------------------------------------

def sprite_cells(sheet, sprites):
    """The 48 x 56 picture's palette indices (-1 where the sprites are see-through), the pieces' sprites placed as the
    levels place them."""
    import numpy as np
    w = 228
    idx = np.fromfile(sheet[:-4] + ".idx", dtype=np.uint8)
    idx = idx[-(len(idx) // w) * w:].reshape(-1, w).astype(int)
    idx[idx == 0] = -1          # index 0 is see-through on these sheets (no drawn pixel uses it)
    full = np.full((56, 48), -1, int)
    for corner, sprite in sprites.items():
        c0, r0 = CORNER[corner]
        x, y = (sprite - 1) % 19 * 12, (sprite - 1) // 19 * 14
        full[r0:r0 + 28, c0:c0 + 24] = idx[y:y + 28, x:x + 24]
    return full


def camera_coverage(objects, w, h, origin=(0.0, 0.0)):
    """Which pixels of a w x h picture (its top left corner at origin + (-w/2, h/2)) the game's camera sees the
    objects at, relative to the ground: a ray down the camera's line of sight through each pixel's middle."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in objects]
    d = Vector((0.0, TILT, -1.0)).normalized()
    out = []
    for r in range(h):
        row = []
        for c in range(w):
            x, y = origin[0] - w / 2 + c + 0.5, origin[1] + h / 2 - (r + 0.5)
            z0 = 120.0
            start = Vector((x, y - z0 * TILT, z0))
            row.append(any(t.ray_cast(start, d)[0] is not None for t in trees))
        out.append(row)
    return out


# --- Build ---------------------------------------------------------------------------------------------------------

def export_piece(whole, m, name, box, options, cells, corner):
    out = mk.outdir(options)
    parts = [p for p in (cut(src, box, cap_of(src, m)) for src in whole) if p is not None]
    drop_unused(parts)
    centre = ((box[0] + box[1]) / 2, (box[2] + box[3]) / 2)
    mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0)))
    bpy.context.view_layer.update()
    triangulate(parts)
    if "stats" in options:
        for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:10]:
            print("    %-16s %6d" % (obj.name, mk.triangles([obj])))
    parts = [join(parts, name)]
    parts[0].data.name = name
    for src in whole:
        src.hide_render = True
    if cells is not None:
        c0, r0 = CORNER[corner]
        mask = [[cells[r0 + r][c0 + c] >= 0 for c in range(24)] for r in range(28)]
        mk.compare("%s (top view)" % name, mk.coverage(parts, 24, 28), mask)
        mk.compare("%s (game camera)" % name, camera_coverage(parts, 24, 28), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(name, parts, os.path.join(out, name + ".glb"))
    if "preview" in options and options.get("pieces"):
        mk.preview(options["preview"] + name, parts)
    for obj in parts:
        data = obj.data
        bpy.data.objects.remove(obj)
        if data.users == 0:
            bpy.data.meshes.remove(data)
    for src in whole:
        src.hide_render = False


def model_name(corner, look):
    base = "track_carrier_" + corner
    if look == "rest":
        return base
    if look == "damaged":
        return base + "_damaged"
    return "%s_%d" % (base, SPRITES["roll"][corner])


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    looks = options["looks"].split(",") if "looks" in options else ["rest", "roll", "damaged"]
    sheet = os.path.join(options["check"], "enemy_S.png") if "check" in options else None
    for look in looks:
        names = [model_name(c, look) for c, _ in PIECES]
        if only and not any(n in only for n in names):
            continue
        k.reset()
        whole, m = build_whole(look)
        if look == "damaged":
            damage(whole, m)
        # Every mesh triangulated before the cuts: the cut pieces' normals are looked up on the whole's triangles,
        # and a --check render tessellates n-gons its own way (the output then changed with --check).
        triangulate(whole)
        cells = sprite_cells(sheet, SPRITES[look]).tolist() if sheet else None
        if "stats" in options:
            print("whole (%s): %d triangles" % (look, mk.triangles(whole)))
        if cells is not None:
            mask = [[v >= 0 for v in row] for row in cells]
            mk.compare("whole %s (top view)" % look, mk.coverage(whole, 48, 56), mask)
            mk.compare("whole %s (game camera)" % look, camera_coverage(whole, 48, 56), mask)
        if "preview" in options:
            mk.preview(options["preview"] + "carrier_" + look, whole, size=(48, 56), scale=8, distance=1.9)
        if "whole" in options:
            copies = []
            for src in whole:
                c = src.copy()
                c.data = src.data.copy()
                bpy.context.scene.collection.objects.link(c)
                copies.append(c)
            triangulate(copies)
            mk.export(copies, options["whole"] + look + ".glb")
            for c in copies:
                bpy.data.objects.remove(c)
        for corner, box in PIECES:
            name = model_name(corner, look)
            if only and name not in only:
                continue
            export_piece(whole, m, name, box, options, cells, corner)


if __name__ == "__main__":
    build()
