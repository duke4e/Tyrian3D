"""IXMUCANE's and SAWBLADES' big purple glass dome (sheet R sprites 5 7 9 above 43 45 47 above 81 83 85, 2x2 each: one
72 x 84 picture; ground layer; enemies 299 300 301 above 296 297 298 above 293 294 295 of episode 3, armour 30 each, not
animated, no damaged look: their dgr is 0), polished (2026-10-21; it replaces wave3_af_domes.py's big_dome(), a city
of random tower blocks under a pixel-painted dark shell).

The levels always put the nine together (event 6 each, one link: 299 300 301 at (x, y - 56), (x + 24, y - 56),
(x + 48, y - 56), 296 297 298 28 pixels lower, 293 294 295 at (x, y) to (x + 48, y); IXMUCANE's events 461-469 at
2876, 512-529 at 3184 (two domes 96 pixels apart), 542-550 at 3352 and 576-584 at 3548 (at x 186, the screen's right
side), SAWBLADES' at 636, 1084, 3044, 3128, 4472 and 4724). No episode 6 level takes them (REEF takes only IXMUCANE's
boss), no other enemy shows any of the nine sprites (catalog.json, the launched enemies too), and none of them is
another sprite's pixels mirrored, turned or in other ramps.

As the sprites and their 4x upscales draw it (columns c 0-71 and rows r 0-83 of the picture): an egg of purple glass
60 x 66 pixels (columns 2-62 of rows 2-68, broadest low down), drawn on squares of the levels' dark brown dirt and
its shadow to the lower left (the map's: left out; the 3D ground shows the dirt, the game casts the shadow). Through
clear glass in its middle a city of slab towers in blue-grey (ramp 6, shades 0x60-0x6e), drawn as a 3/4 view would
draw them: tall narrow fronts outlined in black, each under a lighter roof, rising towards the back to a spire
(columns 30-34, its roof at rows 9-13) with the tallest towers either side of it (columns 26-30 and 38-44, roofs at
row 20), lower ones round them (columns 10-15 at row 24, 15-19 at 28, 35-39 at 28, 19-23 at 32, 27-31 at 38), a broad
lit block at the front right (columns 33-44 of rows 42-52), lower blocks in front, a few lit windows. The glass is
purple where no city shows through it: over the back (rows 2-25 above the skyline: lighter to the left, 0x56-0x5a,
darker to the right, 0x52-0x55), round the sides and in a dark band along its foot at the front (rows 58-67, 0x50-
0x54); a big white glint up and to the left (white 0x5f, 0x6e, 0x0e round pixel (22, 17), in a pale halo out to about
5 pixels) and a pale crescent of reflected light along its right edge, from the top right (row 12) down to the
bottom right (row 60), brightest at the right (0x5c-0x5e at column 60 of rows 41-47), a broader faint sheen inside it
on the upper right.

Built as such a dome, in the family of the small glass dome (polish_glass_city.py: the same kind of collar, floor,
bevelled blocks with roof rims, rooftop units and lit skylights, lit windows in rows (its windows()), glass bands and
glint films):
- a purple collar round the egg's foot (fitted to the sprite's outline: a polar Fourier series, EGG), reaching SKIRT
  below the ground, so that it stands on the terrain with height=-4 (as the small dome does) or without it; a floor of
  dark streets inside it;
- the city: slab towers on deep plans, stepped back in tiers (each tier narrower and taller than the one in front of
  it; the top tier's roof in the tower's lit shade, the lower tiers' roofs darker), in the sprite's columns, laid out
  for the game's camera (20 degrees from straight down, from the bottom of the screen): a roof at height h is seen
  TAN * h further up the screen than it stands, so each tower's plan is moved back by that much and its highest roof
  shows where the sprite draws its roof, its front walls (lit windows in rows) and lower tiers in front of it where the
  sprite draws its front; lower blocks between them and in front; the spire, the tallest (21 pixels), carries a white
  beacon on a mast on a lantern storey; all of them kept GAP under the glass;
- the glass: a single sheet (the game draws both its sides) over the egg, a superellipse profile GLASS_H high (28 at
  its crown), clear where the camera sees the city through it (by a map of the towers as the camera sees them, grown,
  its gaps closed and smoothed: CITY map), purple elsewhere and dark at its foot (the outer RIM of its radius), the
  band edges cut along smooth contours; its far side (the steep back wall, which the camera sees only from inside,
  through the near side) clear: the game lights the inside of a sheet as facing the camera (its shaders turn back
  faces' normals round), dark, and the pieces are drawn one after another, so a dark far side would darken the near
  glass in patches bounded by the cut lines, depending on which piece is drawn first;
- the glint (a white core in a sheen and stacked faint halos, reaching further up and to the left) and the crescent (a
  faint band and a sheen along the right rim, white where it is brightest) and the broad faint sheen on the upper
  right: films lying on the glass where the camera sees the sprite's, lit a little (emission well under 1).
Its parts are built whole and cut along the sprites' edges into the nine pieces, each moved so its sprite's centre
is its origin: the solids with caps coloured as their inside (the buildings' and the floor's in the streets' dark, the
collar's in its own purple; flat, facing out of their cut), so that a piece fading in (the game draws it see-through,
both sides, without depth writes) or shot away shows a dark inside where it was cut rather than lit walls; the glass
and its films cut open (no caps). Each piece is one mesh (triangulated before export, polish_k_pod.triangulate), its
opaque faces first, then its see-through ones in the order the game should blend them (it draws a model's see-through
materials in their order, then their triangles in order, without depth writes or culling): the clear glass (with the
far side), the dark, the purple, then the films (halo, sheen, white); within each the faces far from the camera first.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the
whole's origin is the picture's middle: P(c, r) turns the picture's pixel edges (column c, row r) into these
coordinates (x = c - 36, y = 42 - r). The pieces' centres: tl (-24, 28), tc (0, 28), tr (24, 28), ml (-24, 0), mc
(0, 0), mr (24, 0), bl (-24, -28), bc (0, -28), br (24, -28).

models.cfg: model purple_dome_tl ... _br enemies/purple_dome_*.glb origin (unchanged); sprite r 5 purple_dome_tl yaw=0
height=-4 and so on for the nine (height=-4 added: it stands on the terrain, as the small dome does).

Replaces wave3_af_domes.py (all of it: the big dome is all it still builds; nothing imports it), wave3_af_art.py's
BIG_DOME (only wave3_af_domes.py reads it) and the parts of wave3_af_kit.py only the domes used: glass(),
mask_where(), the open glass shells' cut (GLASS, cut_open(), _cut_box, cut_box() and run()'s swap of sh.cut_box:
run = v.run does the same for wave3_af.py and wave3_af_heap.py, which have no glass shells), dome_shell(),
polygon_reach(), shell_height(), blocks(), coverage() and tower(); wave3_af.py and wave3_af_heap.py, which import the
kit and the art, use none of these.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each piece against the dome's pixels in enemy_R.png), --preview <prefix> (the whole's and each piece's
top and 3/4 views), --only <piece,...>, --whole <file.glb> (the uncut dome, for looking at).
"""
import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_glass_city import windows  # noqa: E402  (the small dome's lit windows in rows)
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_ixm_dock import Shading  # noqa: E402  (normals looked up on the coplanar source triangle)
from polish_glass_globe import reorder  # noqa: E402  (a mesh rebuilt with its faces in a given order)

# The pieces: (name, sprite, the box it covers in the whole's coordinates (x0, x1, y0, y1)).
PIECES = [("purple_dome_tl", 5, (-36.0, -12.0, 14.0, 42.0)), ("purple_dome_tc", 7, (-12.0, 12.0, 14.0, 42.0)),
          ("purple_dome_tr", 9, (12.0, 36.0, 14.0, 42.0)), ("purple_dome_ml", 43, (-36.0, -12.0, -14.0, 14.0)),
          ("purple_dome_mc", 45, (-12.0, 12.0, -14.0, 14.0)), ("purple_dome_mr", 47, (12.0, 36.0, -14.0, 14.0)),
          ("purple_dome_bl", 81, (-36.0, -12.0, -42.0, -14.0)), ("purple_dome_bc", 83, (-12.0, 12.0, -42.0, -14.0)),
          ("purple_dome_br", 85, (12.0, 36.0, -42.0, -14.0))]
SPRITE_AT = {5: (0, 0), 7: (24, 0), 9: (48, 0), 43: (0, 28), 45: (24, 28), 47: (48, 28), 81: (0, 56), 83: (24, 56),
             85: (48, 56)}  # top left corners in the 72 x 84 picture


def P(c, r):
    """A pixel edge of the 72 x 84 picture (column c, row r) in the whole's coordinates."""
    return (c - 36.0, 42.0 - r)


# The game's camera: 20 degrees from straight down, from the bottom of the screen. A point TAN * z above the ground is
# seen where the ground is that much further up the screen.
VIEW_TILT = 20.0
TAN = math.tan(math.radians(VIEW_TILT))
TOWARDS_VIEW = Vector((0.0, -math.sin(math.radians(VIEW_TILT)), math.cos(math.radians(VIEW_TILT))))

# The egg's outline (the outer edge of its glass and city pixels, half the black outline in): its middle and its
# distance from it at angle a, r(a) = c0 + sum(c[2n-1] cos(n a) + c[2n] sin(n a)) (fitted to the pixels, 0.37 px rms).
EGG_C = (-4.088, 5.364)
EGG = (31.264, -0.194, -0.44, -1.569, -0.338, -0.187, -1.885, -0.203, 0.141)
SKIRT = -4.0                          # how far the collar reaches below the ground (z = 0)
# The collar's cross-section from its outer foot in: (inset from the outline, z).
COLLAR = [(0.0, SKIRT), (0.0, 0.0), (0.0, 0.6), (0.28, 1.18), (0.75, 1.5), (1.4, 1.52), (1.95, 1.2), (2.15, 0.7),
          (2.15, SKIRT)]
FLOOR_IN, FLOOR_Z = 2.05, 0.32        # the streets inside it
# The glass: its foot's inset from the outline and its height (on the collar's top), its height above the foot, its
# profile's power (a superellipse, fuller than a half ellipsoid).
GLASS_IN, GLASS_Z0, GLASS_H, GLASS_POWER = 1.0, 1.42, 26.6, 2.4
RIM = 0.93                            # the glass is dark beyond this share of its foot's radius
FAR = 0.02                            # faces turned further from the camera than this are the far side
GAP = 1.6                             # the buildings keep this far under the glass
SEGMENTS = 120                        # round the egg

# The city. Towers: (columns c0, c1 (pixel edges), the row where the sprite draws its highest roof's back edge, the
# row of its front's foot (plan), its tiers' heights from the top one down, the top tier's plan depth, its roof's shade,
# options). Each tier below the top one is TIER_IN wider on either side and reaches further forward (the fronts
# spread evenly to the foot's row), its back BACK_STEP behind the one above. Options: "beacon" (the spire's white lamp
# on a mast), "mast" (an antenna this high), "units" (rooftop units on the top tier), "sky" (lit skylights on it),
# "rim" (a roof rim round the top tier).
TIER_IN, BACK_STEP = 0.5, 0.5
TOWERS = [
    # The spire, the tallest, its white beacon on top.
    (30.0, 34.6, 9.4, 27.0, (21.0, 16.5, 11.5), 3.8, "light", {"beacon": True}),
    # The tall towers either side of it.
    (25.6, 30.2, 19.6, 38.5, (15.5, 10.5), 4.2, "light", {"units": 1, "rim": True}),
    (38.4, 44.6, 20.4, 46.0, (16.0, 11.5, 6.5), 4.6, "light", {"units": 2, "sky": 1, "rim": True}),
    # Round them, lower.
    (20.4, 25.4, 22.6, 34.0, (12.0, 8.0), 3.4, "mid", {"units": 1, "rim": True}),
    (10.4, 15.2, 24.2, 48.5, (12.5, 8.0), 4.0, "light", {"units": 1, "mast": 1.6, "rim": True}),
    (15.4, 19.6, 28.0, 47.4, (9.5, 6.0), 3.0, "light", {"rim": True}),
    (34.8, 38.6, 27.8, 42.0, (11.0, 7.0), 3.2, "light", {"units": 1, "rim": True}),
    (30.8, 34.8, 26.4, 40.5, (9.5,), 0.0, "mid", {"units": 1, "sky": 1, "rim": True}),
    (19.4, 23.6, 32.0, 45.0, (9.0,), 0.0, "mid", {"units": 2, "rim": True}),
    (27.4, 31.6, 38.0, 52.0, (8.0, 5.0), 3.4, "light", {"units": 1, "rim": True}),
    (44.6, 48.2, 30.0, 38.5, (6.5,), 0.0, "dark", {"units": 1, "rim": True}),
    (47.4, 53.6, 38.2, 51.0, (7.0,), 0.0, "dark", {"units": 2, "sky": 1, "rim": True}),
    (6.8, 10.8, 41.0, 51.0, (6.0,), 0.0, "mid", {"units": 1, "rim": True}),
    # The broad lit block at the front right.
    (33.0, 44.6, 42.6, 53.0, (6.2,), 0.0, "mid", {"units": 2, "sky": 3, "rim": True}),
    # Low blocks in front.
    (12.6, 19.4, 47.4, 55.6, (4.0,), 0.0, "dark", {"units": 1, "rim": True}),
    (19.8, 26.6, 46.6, 57.2, (5.0,), 0.0, "mid", {"units": 1, "sky": 1, "rim": True}),
    (26.8, 32.4, 51.0, 58.2, (3.6,), 0.0, "dark", {"units": 1, "rim": True}),
    (35.6, 46.2, 52.6, 58.6, (3.2,), 0.0, "dark", {"units": 2, "rim": True}),
    (46.6, 52.4, 50.6, 56.4, (2.8,), 0.0, "mid", {"rim": True}),
    (8.6, 12.4, 50.4, 55.4, (2.6,), 0.0, "dark", {}),
    (53.4, 56.4, 40.4, 50.0, (3.4,), 0.0, "mid", {"rim": True}),
    (44.6, 47.4, 38.6, 49.0, (4.4,), 0.0, "mid", {"units": 1}),
    (23.8, 27.2, 40.2, 47.0, (5.4,), 0.0, "dark", {"units": 1, "rim": True}),
]
SEED = 299
WINDOW_CHANCE = (0.3, 0.45)           # lit windows on low walls, on walls over 4 pixels high

# The glint (the white lens up and to the left): where the camera sees its middle (the picture's pixel edges), and
# its films from the outside in, (radius seen from above, lift off the glass, material, offset (x, y) of its middle):
# faint halos stacked so that it fades outwards (the outer ones reaching further up and to the left, as the sprite's
# lighter glass round it does), a sheen, the white core.
GLINT = ((22.0, 17.0), [(8.2, 0.016, "halo", -1.4, 0.8), (6.8, 0.02, "halo", -0.7, 0.4), (5.6, 0.028, "halo", 0, 0),
                        (4.6, 0.036, "halo", 0, 0), (3.8, 0.045, "sheen", 0, 0), (2.9, 0.06, "glint", 0, 0)])
# The crescent along the right rim and the broad faint sheen inside it on the upper right: bands of films (angles
# round the egg's middle in degrees from the right, counter-clockwise; radial span in shares of the glass's foot
# radius; lift; material; how sharply the band narrows to its ends): a broad faint band, a sheen inside it, the white
# core where it is brightest (the sprite's column 60 of rows 41-47).
CRESCENT = [(-60.0, 64.0, 0.885, 0.978, 0.02, "halo", 0.7), (-50.0, 48.0, 0.915, 0.972, 0.035, "sheen", 0.7),
            (-24.0, -2.0, 0.928, 0.958, 0.06, "glint", 0.8), (20.0, 84.0, 0.6, 0.78, 0.022, "halo", 1.0)]
# The map of the towers as the camera sees them, for clearing the glass over the city: its cell (pixels), how far it
# reaches past the towers, the gaps it closes between them, its blur (pixels).
MAP_CELL, MAP_GROW, MAP_CLOSE, MAP_BLUR = 0.25, 0.25, 1.2, 0.8


def materials():
    glow = k.level_palette()

    def mat(name, index, metallic=0.4, roughness=0.4, strength=0.0, alpha=None):
        if strength > 0:
            return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=glow[index],
                              emission_strength=strength, alpha=alpha)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, alpha=alpha)
    return {
        "collar": mat("dome_collar", 0x56, 0.5, 0.32),
        "street": mat("dome_street", 0x61, 0.2, 0.6),
        "wall": mat("dome_wall", 0x62, 0.25, 0.5),
        "light": mat("dome_roof_light", 0x68, 0.25, 0.42),
        "mid": mat("dome_roof", 0x67, 0.25, 0.45),
        "dark": mat("dome_roof_dark", 0x66, 0.25, 0.48),
        "body": mat("dome_roof_low", 0x64, 0.25, 0.5),
        "window": mat("dome_window", 0x89, 0.0, 0.3, strength=0.5),
        "beacon": mat("dome_beacon", 0x0f, 0.0, 0.25, strength=0.6),
        "glass_dark": mat("dome_glass_dark", 0x53, 0.0, 0.3, alpha=0.85),
        "glass_purple": mat("dome_glass_purple", 0x55, 0.0, 0.14, alpha=0.8),
        "glass": mat("dome_glass", 0x68, 0.0, 0.08, alpha=0.08),
        "halo": mat("dome_halo", 0x5c, 0.0, 0.08, strength=0.15, alpha=0.16),
        "sheen": mat("dome_sheen", 0x5d, 0.0, 0.08, strength=0.3, alpha=0.4),
        "glint": mat("dome_glint", 0x5f, 0.0, 0.05, strength=0.55, alpha=0.92),
    }


# The see-through materials in the order the game should draw them (after the opaque ones).
BLEND_ORDER = ["glass", "glass_dark", "glass_purple", "halo", "sheen", "glint"]


# --- The egg and the glass ------------------------------------------------------------------------------------------

def egg_reach(a):
    """The outline's distance from the egg's middle at angle a (radians)."""
    r = EGG[0]
    for n in range(1, (len(EGG) - 1) // 2 + 1):
        r += EGG[2 * n - 1] * math.cos(n * a) + EGG[2 * n] * math.sin(n * a)
    return r


def egg_point(a, inset, z):
    r = egg_reach(a) - inset
    return Vector((EGG_C[0] + r * math.cos(a), EGG_C[1] + r * math.sin(a), z))


def glass_t(x, y):
    """How far out (x, y) is on the glass: the share of its foot's radius in that direction."""
    dx, dy = x - EGG_C[0], y - EGG_C[1]
    return math.hypot(dx, dy) / (egg_reach(math.atan2(dy, dx)) - GLASS_IN)


def glass_height(x, y):
    """The glass's height above (x, y) (its foot's height outside it)."""
    t = glass_t(x, y)
    if t >= 1:
        return GLASS_Z0
    return GLASS_Z0 + GLASS_H * (1 - t ** GLASS_POWER) ** (1 / GLASS_POWER)


def shell_point(t, a, lift=0.0):
    """The point on the glass at t (a share of its foot's radius) and angle a, lifted along the glass's normal."""
    r = t * (egg_reach(a) - GLASS_IN)
    x, y = EGG_C[0] + r * math.cos(a), EGG_C[1] + r * math.sin(a)
    z = glass_height(x, y) if t < 1 else GLASS_Z0
    if lift == 0.0:
        return Vector((x, y, z))
    return Vector((x, y, z)) + shell_normal(x, y) * lift


def shell_normal(x, y):
    """The glass's outward normal over (x, y) (from the height's slope; at its foot, outward)."""
    e = 0.05
    t = glass_t(x, y)
    if t > 0.995:
        a = math.atan2(y - EGG_C[1], x - EGG_C[0])
        return Vector((math.cos(a), math.sin(a), 0.0))
    dzdx = (glass_height(x + e, y) - glass_height(x - e, y)) / (2 * e)
    dzdy = (glass_height(x, y + e) - glass_height(x, y - e)) / (2 * e)
    return Vector((-dzdx, -dzdy, 1.0)).normalized()


def seen_at(co):
    """Where the camera sees a point: the ground point (x, y) behind it."""
    return (co.x, co.y + TAN * co.z)


def near_point(sx, sy):
    """The point of the glass's near side the camera sees at the ground point (sx, sy), or None."""
    # Along x = sx, from the egg's front to where the near side's view turns back (the outline as seen).
    lo, hi = None, None
    ys = [EGG_C[1] - 40.0 + 0.1 * i for i in range(801)]
    best = None
    for y in ys:
        if glass_t(sx, y) >= 1.0:
            continue
        s = y + TAN * glass_height(sx, y)
        if best is None or s > best[1]:
            best = (y, s)
        if lo is None:
            lo = y
    if lo is None or best is None or sy > best[1]:
        return None
    lo, hi = lo, best[0]
    for _ in range(50):
        mid = (lo + hi) / 2
        if mid + TAN * glass_height(sx, mid) < sy:
            lo = mid
        else:
            hi = mid
    y = (lo + hi) / 2
    return Vector((sx, y, glass_height(sx, y)))


# --- The parts ------------------------------------------------------------------------------------------------------

def collar(m):
    """The purple collar round the dome's foot, its top rounded, closed underneath."""
    rings = [[egg_point(2 * math.pi * j / SEGMENTS, inset, z) for j in range(SEGMENTS)] for inset, z in COLLAR]
    obj = k.loft("collar", rings, m["collar"], cap_start=False, cap_end=False)
    # Closed underneath (a flat ring on the ground), so the cuts can be capped.
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.bridge_loops(bm, edges=[e for e in bm.edges if e.is_boundary])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    k.smooth(obj, 50)
    return obj


def floor(m):
    """The streets: a flat slab inside the collar."""
    rings = [[egg_point(2 * math.pi * j / SEGMENTS, FLOOR_IN, z) for j in range(SEGMENTS)] for z in (0.0, FLOOR_Z)]
    obj = k.loft("floor", rings, m["street"], start_point=(EGG_C[0], EGG_C[1], 0.0),
                 end_point=(EGG_C[0], EGG_C[1], FLOOR_Z))
    k.smooth(obj, 30)
    return obj


def block(name, x0, x1, y0, y1, z0, z1, roof, m, bevel=0.2):
    """A block with chamfered edges, its top in the roof's shade."""
    body = mk.box(name, x0, x1, y0, y1, z0, z1, m["wall"])
    mk.bevel(body, bevel, 1, 35)
    mk.shade(body, 35)
    mk.paint(body, lambda c, n: roof if n.z > 0.8 else None)
    return body


def rim(name, x0, x1, y0, y1, z, mat, width=0.3, height=0.36):
    """A low rim round a roof's edge: a frame (its outer edge 0.1 inside the roof's), one mesh."""
    o = [(x0 + 0.1, y0 + 0.1), (x1 - 0.1, y0 + 0.1), (x1 - 0.1, y1 - 0.1), (x0 + 0.1, y1 - 0.1)]
    i = [(x0 + 0.1 + width, y0 + 0.1 + width), (x1 - 0.1 - width, y0 + 0.1 + width),
         (x1 - 0.1 - width, y1 - 0.1 - width), (x0 + 0.1 + width, y1 - 0.1 - width)]
    z0, z1 = z - 0.05, z + height
    verts = [(x, y, z0) for x, y in o] + [(x, y, z1) for x, y in o] + [(x, y, z1) for x, y in i] + \
            [(x, y, z0) for x, y in i]
    faces = []
    for a in range(4):
        b = (a + 1) % 4
        faces += [(a, b, 4 + b, 4 + a), (4 + a, 4 + b, 8 + b, 8 + a), (8 + a, 8 + b, 12 + b, 12 + a),
                  (12 + a, 12 + b, b, a)]
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def tiers_of(spec):
    """A tower's tiers from the top down: (x0, x1, y0, y1, height) in the whole's coordinates, laid out for the
    game's camera (its highest roof's back edge seen at the sprite's row)."""
    c0, c1, top_row, foot_row, heights, depth, _, _ = spec
    n = len(heights)
    back = top_row + TAN * heights[0]
    front_top = back + depth if n > 1 else foot_row
    out = []
    for i, h in enumerate(heights):
        inset = TIER_IN * (n - 1 - i)
        b = back - BACK_STEP * i
        f = front_top + (foot_row - front_top) * (i / (n - 1)) if n > 1 else foot_row
        (x0, y1), (x1, y0) = P(c0 + inset, b), P(c1 - inset, f)
        out.append((x0, x1, y0, y1, h))
    return out


def clipped(x0, x1, y0, y1, h):
    limit = min(glass_height(x, y) for x in (x0, x1) for y in (y0, y1)) - GAP
    return min(h, limit)


def tower(i, spec, m, rng):
    """A slab tower: its tiers (bevelled blocks), roof rims, rooftop units, lit skylights and windows, the spire's
    beacon; returns the apparent rectangles (as the camera sees them) of its tiers."""
    roof = m[spec[6]]
    opts = spec[7]
    tiers = tiers_of(spec)
    seen = []
    walls = []
    heights = []
    for j, (x0, x1, y0, y1, h) in enumerate(tiers):
        h = clipped(x0, x1, y0, y1, h)
        if h < spec[4][j] - 0.3:
            print("tower %d tier %d clipped by the glass: %.1f -> %.1f" % (i, j, spec[4][j], h))
        heights.append(h)
        # The lower tiers' roofs darker than the top one's (the sprite's fronts are darker than their lit tops).
        tier_roof = roof if j == 0 else m["body"]
        block(f"t{i}_{j}", x0, x1, y0, y1, FLOOR_Z - 0.05, h, tier_roof, m)
        seen.append((x0, x1, y0, y1 + TAN * h))
    for j, (x0, x1, y0, y1, _) in enumerate(tiers):
        h = heights[j]
        low = heights[j + 1] if j + 1 < len(tiers) else FLOOR_Z
        walls += [((x0, y0), (x1, y0), (0, -1), low, h), ((x0, y1), (x0, y0), (-1, 0), low, h),
                  ((x1, y0), (x1, y1), (1, 0), low, h)]
        if (j > 0 or opts.get("rim")) and not (j == 0 and opts.get("beacon")):
            rim(f"t{i}_{j}_rim", x0, x1, y0, y1, h, m["wall"])
    x0, x1, y0, y1, _ = tiers[0]
    top = heights[0]
    for u in range(opts.get("units", 0)):
        w, d = rng.uniform(0.9, 1.5), rng.uniform(0.8, 1.3)
        ux = rng.uniform(x0 + 0.6, max(x0 + 0.6, x1 - 0.6 - w))
        uy = rng.uniform(y0 + 0.6, max(y0 + 0.6, y1 - 0.6 - d))
        uh = rng.uniform(0.45, 0.8)
        unit = mk.box(f"t{i}_unit{u}", ux, ux + w, uy, uy + d, top - 0.05, top + uh, m["wall"])
        mk.bevel(unit, 0.1, 1, 35)
        mk.shade(unit, 35)
        mk.paint(unit, lambda c, n: m["dark"] if n.z > 0.8 else None)
    for s in range(opts.get("sky", 0)):
        w, d = rng.uniform(0.7, 1.1), rng.uniform(0.6, 0.9)
        sx = rng.uniform(x0 + 0.6, max(x0 + 0.6, x1 - 0.6 - w))
        sy = rng.uniform(y0 + 0.6, max(y0 + 0.6, y1 - 0.6 - d))
        mk.box(f"t{i}_sky{s}", sx, sx + w, sy, sy + d, top - 0.05, top + 0.06, m["window"])
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if "mast" in opts:
        mh = min(opts["mast"], glass_height(cx, cy) - top - 0.6)
        k.smooth(mk.tube(f"t{i}_mast", [(cx, cy, top - 0.1), (cx, cy, top + mh)], 0.15, m["light"], 8), 50)
        mk.ball(f"t{i}_mast_tip", (cx, cy, top + mh), (0.26, 0.26, 0.26), m["beacon"], 10, 5)
    if opts.get("beacon"):
        # A crown: a narrow lantern storey on the roof, the mast and the white lamp on it.
        lantern = mk.box(f"t{i}_lantern", x0 + 0.7, x1 - 0.7, y0 + 0.6, y1 - 0.6, top - 0.1, top + 0.55, m["wall"])
        mk.bevel(lantern, 0.12, 1, 35)
        mk.shade(lantern, 35)
        mk.paint(lantern, lambda c, n: m["light"] if n.z > 0.8 else None)
        mh = min(1.0, glass_height(cx, cy) - top - 1.3)
        k.smooth(mk.tube(f"t{i}_beacon_mast", [(cx, cy, top + 0.45), (cx, cy, top + 0.55 + mh)], 0.13, m["light"], 8),
                 50)
        mk.ball(f"t{i}_beacon", (cx, cy, top + 0.7 + mh), (0.36, 0.36, 0.34), m["beacon"], 12, 6)
    chance = WINDOW_CHANCE[1] if top > 4 else WINDOW_CHANCE[0]
    windows(f"t{i}_windows", walls, rng, m, chance)
    return seen


def city_map(rects):
    """The towers as the camera sees them (their apparent rectangles), grown, their gaps closed, blurred: a function
    (x, y) -> 0..1 (1 over the city) on the ground plane."""
    nx, ny = int(72 / MAP_CELL), int(84 / MAP_CELL)
    grid = np.zeros((ny, nx), dtype=np.float64)

    def cell(x, y):
        return (x + 36.0) / MAP_CELL, (42.0 - y) / MAP_CELL
    for x0, x1, y0, y1 in rects:
        c0, r1 = cell(x0 - MAP_GROW, y0 - MAP_GROW)
        c1, r0 = cell(x1 + MAP_GROW, y1 + MAP_GROW)
        grid[max(0, int(round(r0))):min(ny, int(round(r1))), max(0, int(round(c0))):min(nx, int(round(c1)))] = 1.0

    def box_filter(a, radius):
        """The mean over a (2 radius + 1) square round each cell (edges padded)."""
        if radius <= 0:
            return a
        p = np.pad(a, radius, mode="edge")
        c = np.cumsum(np.cumsum(p, axis=0), axis=1)
        c = np.pad(c, ((1, 0), (1, 0)))
        s = 2 * radius + 1
        total = c[s:, s:] - c[:-s, s:] - c[s:, :-s] + c[:-s, :-s]
        return total / (s * s)
    close = int(round(MAP_CLOSE / MAP_CELL))
    grown = (box_filter(grid, close) > 1e-9).astype(np.float64)
    closed = (box_filter(grown, close) > 1 - 1e-9).astype(np.float64)
    closed = np.maximum(closed, grid)
    blur = max(1, int(round(MAP_BLUR / MAP_CELL)))
    field = box_filter(box_filter(closed, blur), blur)

    def at(x, y):
        fc, fr = cell(x, y)
        fc -= 0.5
        fr -= 0.5
        c0, r0 = int(math.floor(fc)), int(math.floor(fr))
        u, v = fc - c0, fr - r0

        def g(r, c):
            if 0 <= r < ny and 0 <= c < nx:
                return field[r, c]
            return 0.0
        return ((g(r0, c0) * (1 - u) + g(r0, c0 + 1) * u) * (1 - v) +
                (g(r0 + 1, c0) * (1 - u) + g(r0 + 1, c0 + 1) * u) * v)
    return at


def glass(m, clear_at):
    """The glass: a superellipse shell over the egg from its foot on the collar up to its crown, one-sided; clear on
    its far side, dark beyond RIM, clear where the camera sees the city through it (clear_at > 0.5), purple elsewhere;
    the band edges cut along smooth contours."""
    ts = [1.0, 0.994, 0.982, 0.962, RIM, 0.895, 0.85, 0.8, 0.745, 0.69, 0.63, 0.565, 0.5, 0.43, 0.355, 0.275, 0.19,
          0.1]
    rings = [[shell_point(t, 2 * math.pi * j / SEGMENTS) for j in range(SEGMENTS)] for t in ts]
    shell = k.loft("glassshell", rings, m["glass"], cap_start=False,
                   end_point=(EGG_C[0], EGG_C[1], GLASS_Z0 + GLASS_H))
    bm = bmesh.new()
    bm.from_mesh(shell.data)
    values = {v: clear_at(*seen_at(v.co)) for v in bm.verts}
    mk.split_along(bm, values, 0.5)
    bm.to_mesh(shell.data)
    bm.free()
    slots = {name: mk.slot_of(shell, m[name]) for name in ("glass_dark", "glass_purple", "glass")}
    for poly in shell.data.polygons:
        c = Vector(poly.center)
        if Vector(poly.normal).dot(TOWARDS_VIEW) < FAR:
            # The far side (the steep back wall, seen only from inside, through the near side): clear, so that what
            # the near side shows doesn't depend on the order the two are drawn in (the game draws the pieces one
            # after the other) and the inside of the back wall (lit from inside: dark) doesn't darken the glass.
            poly.material_index = slots["glass"]
        elif glass_t(c.x, c.y) > RIM:
            poly.material_index = slots["glass_dark"]
        elif clear_at(*seen_at(c)) > 0.5:
            poly.material_index = slots["glass"]
        else:
            poly.material_index = slots["glass_purple"]
    k.smooth(shell, 60)
    return shell


def overlay(name, points_of, rows, cols, mat):
    """A thin film lying on the glass: a grid of points_of(u, v) (u, v in 0..1), its faces facing out."""
    verts = [points_of(i / rows, j / cols) for i in range(rows + 1) for j in range(cols + 1)]
    faces = []
    for i in range(rows):
        for j in range(cols):
            a = i * (cols + 1) + j
            faces.append((a, a + 1, a + cols + 2, a + cols + 1))
    obj = k.mesh_object(name, verts, faces, mat)
    for poly in obj.data.polygons:
        c = Vector(poly.center)
        if poly.normal.dot(shell_normal(c.x, c.y)) < 0:
            poly.flip()
    obj.data.update()
    k.smooth(obj, 80)
    return obj


def highlights(m):
    """The glint up and to the left (a white core in a sheen and stacked faint halos, round the point of the glass
    where the camera sees the sprite's glint), the crescent along the right rim (a faint band and a sheen, white where
    it is brightest) and the broad faint sheen inside it on the upper right: films lying on the glass."""
    (gc, gr), films = GLINT
    gx, gy = P(gc, gr)
    centre = near_point(gx, gy)

    def lens(radius, lift, ox, oy):
        def at(u, v):
            # Polar round the glint's middle, in plan (squashed up the screen as the glass slopes there), then onto
            # the glass.
            rr, a = radius * u, 2 * math.pi * v
            x, y = centre.x + ox + rr * math.cos(a), centre.y + oy + rr * math.sin(a) * 0.9
            t = min(glass_t(x, y), 0.999)
            return shell_point(t, math.atan2(y - EGG_C[1], x - EGG_C[0]), lift)
        return at
    for i, (radius, lift, mat, ox, oy) in enumerate(films):
        overlay("glassshell_glint%d" % i, lens(radius, lift, ox, oy), 3, 32, m[mat])

    def band(lo, hi, w0, w1, lift, taper_power):
        """A band between the angles lo and hi (degrees), its radial span narrowing to its ends."""
        def at(u, v):
            a = math.radians(lo + (hi - lo) * v)
            taper = math.sin(math.pi * v) ** taper_power
            mid = (w0 + w1) / 2
            half = (w1 - w0) / 2 * taper
            return shell_point(mid + (u - 0.5) * 2 * half, a, lift)
        return at
    for i, (a0, a1, t0, t1, lift, mat, taper) in enumerate(CRESCENT):
        overlay("glassshell_band%d" % i, band(a0, a1, t0, t1, lift, taper), 3, max(12, int((a1 - a0) / 2)), m[mat])


# --- Cutting --------------------------------------------------------------------------------------------------------

def cut_solid(source, box_xy, cap_mat):
    """The part of a closed object inside box (x0, x1, y0, y1): its cuts closed by flat caps of cap_mat facing out of
    their cut (given their material as they are made, so a cap a later plane cuts keeps it), the rest keeping its
    own winding and the uncut object's normals. None if nothing of it is inside."""
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
    sides = [(0, x0), (0, x1), (1, y0), (1, y1)]
    bm.normal_update()
    bm.faces.index_update()
    cap_ids = {f.index for f in bm.faces if f.material_index == cap_index and
               any(all(abs(v.co[axis] - at) < 1e-4 for v in f.verts) for axis, at in sides)}
    bm.to_mesh(obj.data)
    bm.free()
    shading = Shading(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.index not in cap_ids:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.normal)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    return obj


def cut_open(source, box_xy, shading):
    """The part of a single surface (the glass, a film) inside box (x0, x1, y0, y1), its cuts left open, its normals
    the uncut one's."""
    x0, x1, y0, y1 = box_xy
    corners = [source.matrix_world @ Vector(c) for c in source.bound_box]
    if (max(c.x for c in corners) <= x0 or min(c.x for c in corners) >= x1 or
            max(c.y for c in corners) <= y0 or min(c.y for c in corners) >= y1):
        return None
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    planes = (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0)))
    for co, no in planes:
        if not bm.faces:
            break
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co, plane_no=no,
                               clear_outer=True)
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    bm.to_mesh(obj.data)
    bm.free()
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.normal)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    return obj


def order_slots(obj, m):
    """The mesh's material slots: the opaque ones first (as they are), then the see-through ones in BLEND_ORDER."""
    mesh = obj.data
    names = [mat.name for mat in mesh.materials]
    rank = {m[r].name: i for i, r in enumerate(BLEND_ORDER)}
    order = sorted(range(len(names)), key=lambda i: (rank.get(names[i], -1), i if names[i] not in rank else 0))
    remap = {old: new for new, old in enumerate(order)}
    mats = [mesh.materials[i] for i in order]
    indices = [remap[p.material_index] for p in mesh.polygons]
    mesh.materials.clear()
    for mat in mats:
        mesh.materials.append(mat)
    mesh.polygons.foreach_set("material_index", indices)
    mesh.update()
    return {mat.name: i for i, mat in enumerate(mats)}


def piece(solids, shells, shadings, name, box, m):
    """One piece: the solids cut and capped, the glass and its films cut open, moved to its sprite's centre,
    triangulated, joined into one mesh, its see-through faces after the opaque ones in the order they blend."""
    parts = []
    for src in solids:
        cap = m["collar"] if src.name.startswith("collar") else m["street"]
        p = cut_solid(src, box, cap)
        if p is not None:
            parts.append(p)
    for src in shells:
        p = cut_open(src, box, shadings[src.name])
        if p is not None:
            parts.append(p)
    drop_unused(parts)
    centre = Vector(((box[0] + box[1]) / 2, (box[2] + box[3]) / 2, 0.0))
    mk.transform(parts, Matrix.Translation(-centre))
    bpy.context.view_layer.update()
    triangulate(parts)
    obj = join(parts, name)
    obj.data.name = name
    slots = order_slots(obj, m)
    see_through = {slots[m[r].name]: i for i, r in enumerate(BLEND_ORDER) if m[r].name in slots}
    view_centre = Vector((EGG_C[0], EGG_C[1], GLASS_Z0)) - centre

    def key(poly):
        if poly.material_index not in see_through:
            return (0, 0, 0.0)
        return (1, see_through[poly.material_index], (Vector(poly.center) - view_centre).dot(TOWARDS_VIEW))
    return reorder(obj, key)


# --- Build ------------------------------------------------------------------------------------------------------------

def build_whole(m):
    rng = random.Random(SEED)
    collar(m)
    floor(m)
    seen = []
    for i, spec in enumerate(TOWERS):
        seen += tower(i, spec, m, rng)
    solids = mk.meshes()
    for obj in solids:
        mk.apply(obj)
    shells = [glass(m, city_map(seen))]
    before = set(mk.meshes())
    highlights(m)
    shells += [o for o in mk.meshes() if o not in before]
    bpy.context.view_layer.update()
    return solids, shells


def dome_pixels(sheets):
    """The dome's own pixels in the 72 x 84 picture (enemy_R.png and its .idx): its glass and city (ramps 5 and 6)
    and the black between and round them (a dark pixel with glass or city on both sides of it along its row or
    column, or next to them); the drawn dirt and the shadow left out."""
    sys.path.insert(0, os.path.join(HERE, "..", ".."))
    from sprite_profile import sprite_indices
    sheet = os.path.join(sheets, "enemy_R.png")
    pic = [[None] * 72 for _ in range(84)]
    for sprite, (c0, r0) in SPRITE_AT.items():
        for r, row in enumerate(sprite_indices(sheet, sprite)):
            for c, v in enumerate(row):
                pic[r0 + r][c0 + c] = v

    def dome(r, c):
        v = pic[r][c] if 0 <= r < 84 and 0 <= c < 72 else None
        return v is not None and v >> 4 in (5, 6)

    def dark(r, c):
        v = pic[r][c]
        return v is not None and v >> 4 == 0
    mask = [[dome(r, c) for c in range(72)] for r in range(84)]
    for r in range(84):
        cols = [c for c in range(72) if dome(r, c)]
        for c in range(72):
            if mask[r][c] or not dark(r, c):
                continue
            rows = [q for q in range(84) if dome(q, c)]
            between = (cols and cols[0] < c < cols[-1]) or (rows and rows[0] < r < rows[-1])
            beside = any(dome(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            mask[r][c] = between or beside
    return mask


def piece_mask(mask, sprite):
    c0, r0 = SPRITE_AT[sprite]
    return [row[c0:c0 + 24] for row in mask[r0:r0 + 28]]


def opaque_coverage(objects, w, h):
    """The top view's coverage with the see-through materials made opaque for it (the dome's own outline)."""
    saved = []
    for mat in sorted({mt for obj in objects for mt in obj.data.materials}, key=lambda mt: mt.name):
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        saved.append((mat, bsdf.inputs["Alpha"].default_value, mat.surface_render_method))
        bsdf.inputs["Alpha"].default_value = 1.0
        mat.surface_render_method = "DITHERED"
    covered = mk.coverage(objects, w, h)
    for mat, alpha, method in saved:
        mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = alpha
        mat.surface_render_method = method
    return covered


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    solids, shells = build_whole(m)
    whole = solids + shells
    print("whole purple dome: %d triangles (solids %d, glass and films %d), %d objects" % (
        mk.triangles(whole), mk.triangles(solids), mk.triangles(shells), len(whole)))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mask = dome_pixels(options["check"]) if "check" in options else None
    if mask:
        mk.compare("whole (R 5 7 9 / 43 45 47 / 81 83 85, the dome)", opaque_coverage(whole, 72, 84), mask)
    if "preview" in options:
        mk.preview(options["preview"] + "purple_dome_whole", whole, size=(72, 84), scale=8, distance=2.4)
    if "whole" in options:
        copies = []
        for src in whole:
            c = src.copy()
            c.data = src.data.copy()
            bpy.context.scene.collection.objects.link(c)
            copies.append(c)
        triangulate(copies)
        mk.export(copies, options["whole"])
        for c in copies:
            bpy.data.objects.remove(c)
    only = options["only"].split(",") if "only" in options else None
    if only == ["none"]:
        return
    shadings = {src.name: Shading(src) for src in shells}
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        obj = piece(solids, shells, shadings, name, box, m)
        for src in whole:
            src.hide_render = True
        if mask:
            mk.compare("%s (R %d)" % (name, sprite), opaque_coverage([obj], 24, 28), piece_mask(mask, sprite))
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj])
        bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
