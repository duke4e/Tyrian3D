"""The Super Arcade's weapon orbs of the power-ups sheet (sprites 7, 9, 11, 13 and 15, 2x2: 24 x 28 cells, the ball
24 x 25 pixels; one frame each), modelled (2026-10-29; until now they had no model and were drawn as HD volumes). In a
Super Arcade game every weapon pick-up an enemy leaves (value over 30000) becomes one of them (tyrian2.c,
superArcadePowerUp: egr 5 + 2n, value 30000 + n, n going round 1-5 from 2, so a level's drops come blue, grey, green,
tan, red, blue ...), the n-th weapon of the ship's five (varz.c SAWeapon's columns R, Bl, Bk, G, P). They drop where the
weapon pick-ups do, beside the front weapons' orbs (polish_powerups_front.py), on the sky layer. models.cfg: model
sa_orb_<colour> items/sa_orb_<colour>.glb and sprite powerups <n> sa_orb_<colour> yaw=0 (no spin: the orb is painted
for the camera, as the other power-ups' orbs are).

- sa_orb_red (7): copper-red glaze, a gem of fire (ramp 7) in its middle
- sa_orb_blue (9): steel-blue glaze, a deep blue gem (ramp 9) with a dark crescent in its lower left
- sa_orb_grey (11): gunmetal glaze, a smoky black gem (the ball's own ramp 0, dark)
- sa_orb_green (13): green glaze, an emerald gem (ramp 12)
- sa_orb_tan (15): golden-brown glaze, a smoky brown gem (the ball's own ramp 1, dark)

The five are one picture shade for shade in other ramps: the ball in ramp 4 (red), 3 (blue), 0 (grey), 2 (green) and 1
(tan), red and grey at the same shades, blue, green and tan a shade lighter (SHADE_UP). But the gem is in another ramp
than the ball in three of them (red's in the fire's ramp 7, blue's in 9, green's in 12; grey's and tan's in the ball's
own, a dark smoky one), and models.cfg's color=sprite gives every palette material of a model the one ramp of the
sprite's frame (render_gpu.c: index = the frame's ramp | the material's shade; layer3d.c sprite_colors: the ramp with
most pixels of shade 3 and up, the ball's): one grey model would show red's gem salmon, blue's pale steel and green's
olive. So, as the other power-ups' orbs are, each is a model of its own in its sprite's palette indices (one script,
one orb, five sets of colours: ORBS), no color=sprite. Blue's gem has a dark crescent across its lower left (the
sprite's ramp 3 0x32-0x34, the other gems only a trace of it): blue's alone gets it, in the gem's own darker blue (its
edge's, as the upscale softens it; the ball's near-black read as a blot). No other enemy shows these sprites.

As the sprites and their 4x upscales draw it: a glazed ball (columns 0-23, rows 1-25: round (0, 0.5), 12 across and 12.5
up either way) with a near-black outline, its face cut into four raised petals, one in each quarter, by a cross of
channels: narrow ones up and down the screen (columns 11-12 between the petals' edges at columns 10 and 13), wide ones
left and right (rows 11-15 between the edges at rows 10 and 16) with two ribs along each (rows 12 and 14); each petal's
inner corner is rounded in a wide arc (radius about 7.7: the sprite's lighter lines from column 10 of row 2 round
through column 6 of row 9 to row 10), so that the four arcs make a four-pointed diamond round the middle, where a
cabochon gem (a diamond cut off at its sides, columns 6-17 and rows 8-18) sits in a dark setting (one pixel round it)
that the petals' corners touch. The petals' inner edges are their lighter lines; the lower right petal is lighter
inside the rim where the light through the glaze gathers (columns 15-19 of rows 19-22); the gem is darkest at its edge,
brightest above its middle on the left (column 10 of rows 11-12), with a second light in its lower right (columns 14-15
of rows 15-16).

The model, built in view space (the game camera's view, the sprite its top view: polish_powerups_front's method) and
tilted into the game's axes with polish_powerups_front.to_world() (the same middle as the other orbs'): one ball whose
surface is moved in along its radius by a height field drawn as the camera sees it (height()): the petals at the
ball's surface, a little domed (PILLOW), their edges rounded off (an S-curve over SHOULDER either side of the outline)
down into the channels (FLOOR deep), the ribs half-rounds standing in the side channels, a bezel ringing the gem's
outline, and a pit under the gem; the mesh is cut along the field's contours (the shoulders', the ribs', the bezel's
and the painted borders) before it is moved, so that the edges are smooth curves rather than the mesh's steps. The gem
is a relief (polish_powerups_front.relief: its outline the sprite's, rounded, its top domed with the ball and rounded
off at its edge) standing in the pit, its top a little over the ball's surface. Painted (palette materials of the
sprite's own indices, at most 14): the petals glazed, glowing faintly in their next shade (so that their side away
from the sun keeps its colour from the slanted camera), their edges two shades lighter (the sprite's lines), the
channels dark, the ribs as the petals, the ball's rim darker in two bands (the outline), the gathered light a
crescent inside the lower right petal's rim (two shades of it), the bezel dark and metallic; the gem in bands from
its edge in (its edge, middle and heart), the light above its middle on the left and in its lower right (GEM_GLARE,
GEM_CAUSTIC: one brightness field, so that the bands nest as soft curves); the bright gems glow 0.18-0.5 in their own
colours, the smoky ones 0.06-0.24. About 8 500 triangles each.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. The game centres the models in
height on their layer.

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir or powerups.png> (each model's
silhouette as the game's camera sees it and from straight above against its sprite), --preview <prefix> (top and
3/4 views), --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402
import polish_powerups_front as front  # noqa: E402  (no side effects: its build() runs only as a script)
from polish_powerups_front import polygon, rounded, round_profile, relief, paint, exact  # noqa: E402

# --- The ball ------------------------------------------------------------------------------------------------------
# Its middle is the other orbs' (front.ORB_C: the sprite's (0, 0.5)), so front.to_world() tilts it the same way.

C = front.ORB_C
R = (11.95, 12.45, 12.0)      # its radii across, up the view and towards the camera

# The mesh before the cuts: a sphere round the view's axis, rings at even distances from the middle as the camera sees
# them (RING_STEP pixels apart from RING_FROM out; a few under the gem), RIM_RINGS (degrees from the view axis) round
# the outline and behind, POINTS points round each.
RING_FROM, RING_STEP = 5.0, 0.9
INNER_RINGS = (1.6, 3.2)
RIM_RINGS = (74.0, 79.0, 84.0, 87.5, 90.0, 94.0, 102.0, 120.0, 150.0)
POINTS = 64

# The petals: the quarters x < -XC, x > XC by y > YT, y < YB, each inner corner rounded by CORNER; their tops domed by
# PILLOW (rising over PILLOW_W from the edge), their edges an S-curve SHOULDER either side of the outline down to the
# channels' floor, FLOOR under the ball's surface.
XC, YT, YB = 1.0, 3.0, -2.0
CORNER = 7.7
PILLOW, PILLOW_W = 0.32, 3.2
SHOULDER = 0.62
FLOOR = 1.05
# The ribs along the side channels (rows 12 and 14): their middles (y), half-width and height over the floor; they start
# RIB_FROM outside the setting's outline.
RIBS = (1.5, -0.5)
RIB_W, RIB_H = 0.5, 0.62
RIB_FROM = 0.35
# The gem's outline: |x| + |y - 0.5| <= GEM_L, |x| <= GEM_X, |y - 0.5| <= GEM_Y, its corners rounded by GEM_ROUND. The
# setting round it: the band out to SETTING (pixels) from that outline, its top BEZEL under the ball's surface, rising
# over BEZEL_IN from the pit (PIT under the surface) and falling over BEZEL_OUT to the floor.
GEM_L, GEM_X, GEM_Y, GEM_ROUND = 7.0, 6.05, 5.55, 1.1
SETTING = 1.0
BEZEL, BEZEL_IN, BEZEL_OUT = 0.22, 0.32, 0.3
PIT = 2.6
# The gem: its top over the ball's surface and its edge's rise (pixels in from the outline, height: a quarter ellipse);
# its colours by a brightness field (gem_light()): the depth inside the outline (0 at it, 1 from GEM_DEEP in) weighed
# GEM_WEIGHTS[0], and two soft lights, above its middle on the left (the glare: middle, radius) and in its lower right
# (the caustic: middle, radii across and up), weighed GEM_WEIGHTS[1] and [2]; the bands' borders in it, edge | middle
# | heart | caustic | glare.
GEM_TOP = 0.7
GEM_EDGE = (5.0, 2.7)
GEM_DEEP = 3.4
GEM_GLARE = (-1.3, 2.3, 2.1)
GEM_CAUSTIC = (2.9, -1.5, 1.9, 1.45)
GEM_WEIGHTS = (0.62, 0.42, 0.3)
GEM_BANDS = [0.2, 0.5, 0.76, 0.9]
# Blue's dark crescent across the gem's lower left (the sprite's 0x32-0x34 in rows 14-17, from columns 12-13 down to
# columns 8-10): a band from the right of the gem's middle down to its lower left edge, its corners rounded.
GEM_CRESCENT = [(2.1, 0.1), (2.0, -1.5), (1.0, -2.5), (-0.6, -3.4), (-1.7, -3.9), (-3.4, -3.8), (-3.9, -3.0),
                (-3.2, -2.1), (-1.6, -1.5), (-0.3, -1.0), (0.6, -0.1)]

# How the ball is painted as the camera sees it (u, v: across and up over its outline, -1..1; rho their length): the
# rim (rho over RIM: the outline) and the outer band (over OUTER); the light gathering inside the lower right petal's
# rim: crescents (part, width at their middle, half their span in degrees) round CAUSTIC_MIDDLE degrees; the petals'
# edges lighter from EDGE_IN inside their outline to EDGE_OUT outside it.
RIM, OUTER = 0.93, 0.85
CAUSTIC_MIDDLE = -50.0
CAUSTIC = [("caustic", 0.22, 40.0), ("caustic_core", 0.12, 26.0)]
EDGE_IN, EDGE_OUT = 1.05, -0.12

# The five orbs: (sprite, the ball's ramp, its shades' offset, the gem's palette indices (edge, middle, heart, glare,
# caustic) and their glows, the crescent).
SHADE_UP = 1
ORBS = {
    "sa_orb_red": (7, 4, 0, (0x73, 0x77, 0x7a, 0x7d, 0x7b), (0.18, 0.26, 0.36, 0.48, 0.42), False),
    "sa_orb_blue": (9, 3, SHADE_UP, (0x95, 0x97, 0x9a, 0x9d, 0x9b), (0.2, 0.28, 0.38, 0.5, 0.44), True),
    "sa_orb_grey": (11, 0, 0, (0x01, 0x03, 0x05, 0x09, 0x07), (0.06, 0.1, 0.15, 0.24, 0.2), False),
    "sa_orb_green": (13, 2, SHADE_UP, (0xc1, 0xc4, 0xc8, 0xcc, 0xc9), (0.18, 0.26, 0.36, 0.48, 0.42), False),
    "sa_orb_tan": (15, 1, SHADE_UP, (0x12, 0x14, 0x17, 0x1b, 0x18), (0.06, 0.1, 0.15, 0.24, 0.2), False),
}
# (palette shade before the offset, the shade of its glow, the glow's strength, metallic, roughness) of each part of
# the ball.
BALL_FINISH = {
    "petal": (7, 8, 0.14, 0.05, 0.28),
    "edge": (9, 10, 0.16, 0.05, 0.26),
    "floor": (3, 4, 0.06, 0.15, 0.42),
    "rib": (7, 8, 0.12, 0.1, 0.3),
    "outer": (5, 6, 0.12, 0.05, 0.28),
    "rim": (1, 2, 0.06, 0.2, 0.3),
    "caustic": (9, 10, 0.22, 0.1, 0.22),
    "caustic_core": (11, 12, 0.3, 0.1, 0.22),
    "bezel": (1, 2, 0.0, 0.55, 0.3),
}


def smoothstep(e0, e1, t):
    """0 below e0, 1 above e1, an S-curve (half a cosine) between."""
    s = np.clip((np.asarray(t, float) - e0) / (e1 - e0), 0.0, 1.0)
    return 0.5 - 0.5 * np.cos(np.pi * s)


def smax(a, b, r=0.25):
    """The larger of a and b, rounded where they meet."""
    h = np.clip(0.5 + 0.5 * (a - b) / r, 0.0, 1.0)
    return b + (a - b) * h + r * h * (1 - h)


def smin(a, b, r=0.25):
    return -smax(-a, -b, r)


def petal_distance(x, y):
    """The signed distance to the petals (inside < 0): the four quarters, each inner corner rounded by CORNER."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    best = np.full(np.broadcast(x, y).shape, np.inf)
    for qx in (-x - XC, x - XC):
        for qy in (y - YT, YB - y):
            a, b = CORNER - qx, CORNER - qy
            outside = (a > 0) | (b > 0)
            d = np.where(outside, np.hypot(np.maximum(a, 0.0), np.maximum(b, 0.0)), np.maximum(a, b)) - CORNER
            best = np.minimum(best, d)
    return best


def gem_points():
    """The gem's outline before rounding: the diamond |x| + |y'| <= GEM_L cut off at |x| = GEM_X and |y'| = GEM_Y."""
    cy = C.y
    L, X, Y = GEM_L, GEM_X, GEM_Y
    return [(X, cy + L - X), (X, cy - (L - X)), (L - Y, cy - Y), (-(L - Y), cy - Y), (-X, cy - (L - X)),
            (-X, cy + L - X), (-(L - Y), cy + Y), (L - Y, cy + Y)]


GEM = rounded(polygon(gem_points()), GEM_ROUND)
GEM_EXACT = exact(GEM)


def ball_z(x, y):
    """The height (towards the camera) of the ball's front at view (x, y); 0 beyond its outline."""
    u = (np.asarray(x, float) - C.x) / R[0]
    v = (np.asarray(y, float) - C.y) / R[1]
    return R[2] * np.sqrt(np.maximum(0.0, 1.0 - u * u - v * v))


def rib_field(x, y):
    """How far (in parts of RIB_W) a point is from the nearest rib's middle."""
    y = np.asarray(y, float)
    return np.minimum.reduce([np.abs(y - r) for r in RIBS]) / RIB_W


def height(x, y):
    """The surface's height over the ball's (radially, pixels; negative: sunk) at view (x, y), from the fields."""
    d = petal_distance(x, y)
    g = GEM(x, y)
    pillow = PILLOW * smoothstep(0.0, PILLOW_W, -d)
    petal = -FLOOR + (FLOOR + pillow) * (1.0 - smoothstep(-SHOULDER, SHOULDER, d))
    t = rib_field(x, y)
    rib = -FLOOR + RIB_H * np.sqrt(np.clip(1.0 - t * t, 0.0, 1.0)) * smoothstep(SETTING, SETTING + RIB_FROM + 0.4, g)
    land = smax(petal, rib, 0.18)
    bezel = -FLOOR + (FLOOR - BEZEL) * (1.0 - smoothstep(SETTING - BEZEL_OUT, SETTING + BEZEL_OUT, g))
    land = smax(land, bezel, 0.12)
    pit = -PIT + 9.0 * smoothstep(0.0, BEZEL_IN, g)
    return smin(land, pit, 0.12)


def view_of(x, y, z):
    """A point's place in the ball's view: (u, v, rho, angle in degrees from +x, counter-clockwise)."""
    u = (np.asarray(x, float) - C.x) / R[0]
    v = (np.asarray(y, float) - C.y) / R[1]
    return u, v, np.hypot(u, v), np.degrees(np.arctan2(v, u))


def crescent(x, y, z, width, span):
    """Over 0 inside a crescent along the inside of the rim, width wide at its middle, tapering to its ends span
    degrees either way of CAUSTIC_MIDDLE (on the side the camera sees)."""
    _, _, rho, angle = view_of(x, y, z)
    a = ((angle - CAUSTIC_MIDDLE + 180.0) % 360.0 - 180.0) / span
    return np.where(np.asarray(z) > 0.5, rho - RIM + width * np.maximum(0.0, 1.0 - a * a), -1.0)


def ball_materials(ramp, offset):
    pal = k.level_palette()
    mats = {}
    for key, (shade, glow, strength, metallic, roughness) in BALL_FINISH.items():
        s, g = min(15, shade + offset), min(15, glow + offset)
        if strength > 0:
            mats[key] = k.material(f"sa{ramp}_{key}", palette=16 * ramp + s, metallic=metallic, roughness=roughness,
                                   emission=pal[16 * ramp + g], emission_strength=strength)
        else:
            mats[key] = k.material(f"sa{ramp}_{key}", palette=16 * ramp + s, metallic=metallic, roughness=roughness)
    return mats


def sphere():
    """The ball's sphere before the cuts (a bmesh): rings round the view's axis, the front pole towards the camera."""
    rhos = list(INNER_RINGS)
    r = RING_FROM
    while r < R[0] * math.sin(math.radians(RIM_RINGS[0])) - 0.2:
        rhos.append(r)
        r += RING_STEP
    thetas = [math.asin(min(1.0, q / R[0])) for q in rhos] + [math.radians(a) for a in RIM_RINGS]
    bm = bmesh.new()
    front_pole = bm.verts.new((C.x, C.y, R[2]))
    rings = []
    for th in thetas:
        s, c = math.sin(th), math.cos(th)
        rings.append([bm.verts.new((C.x + R[0] * s * math.cos(2 * math.pi * j / POINTS),
                                    C.y + R[1] * s * math.sin(2 * math.pi * j / POINTS), R[2] * c))
                      for j in range(POINTS)])
    back_pole = bm.verts.new((C.x, C.y, -R[2]))
    n = POINTS
    for j in range(n):
        bm.faces.new((front_pole, rings[0][j], rings[0][(j + 1) % n]))
    for a, b in zip(rings, rings[1:]):
        for j in range(n):
            bm.faces.new((a[j], b[j], b[(j + 1) % n], a[(j + 1) % n]))
    for j in range(n):
        bm.faces.new((rings[-1][j], back_pole, rings[-1][(j + 1) % n]))
    return bm


def split_front(bm, values, threshold):
    """polish_item_kit.split_along for the side the camera sees: cuts the faces along the contour where the vertex
    values cross threshold, only across edges with both ends in front (view z over FRONT_Z)."""
    made = set()
    for e in list(bm.edges):
        a, b = e.verts
        if a.co.z < FRONT_Z or b.co.z < FRONT_Z:
            continue
        fa, fb = values[a], values[b]
        if (fa - threshold) * (fb - threshold) < 0:
            _, v = bmesh.utils.edge_split(e, a, (threshold - fa) / (fb - fa))
            values[v] = threshold
            made.add(v)
    for f in list(bm.faces):
        ends = [v for v in f.verts if v in made]
        if len(ends) == 2 and not any(ends[1] in e.verts for e in ends[0].link_edges):
            bmesh.utils.face_split(f, ends[0], ends[1])
    return made


def cut(bm, field, levels):
    """Cuts the faces along the contours field(x, y, z) = level, on the side the camera sees."""
    for t in levels:
        verts = bm.verts[:]
        co = np.array([v.co for v in verts])
        values = field(co[:, 0], co[:, 1], co[:, 2])
        split_front(bm, dict(zip(verts, values.tolist())), t)


# The height field fades out behind the outline (view z from BACK_FADE to 0), where the camera never looks, and its
# sunk parts towards the outline (rho from RIM_FADE[0] to [1]), so that the channels don't notch it; the cuts stop at
# FRONT_Z.
BACK_FADE = -2.5
RIM_FADE = (0.88, 0.995)
FRONT_Z = -1.0


def ball(ramp, offset):
    """The ball in view space: the sphere cut along the field's contours, moved in along its radius by height() and
    painted. Returns the object."""
    mats = ball_materials(ramp, offset)
    keys = list(mats)
    bm = sphere()
    petal = lambda x, y, z: petal_distance(x, y)  # noqa: E731
    gem = lambda x, y, z: GEM(x, y)  # noqa: E731
    cut(bm, petal, [-SHOULDER, 0.0, SHOULDER, -EDGE_IN, EDGE_OUT])
    cut(bm, lambda x, y, z: rib_field(x, y) + 4.0 * np.maximum(0.0, SHOULDER - petal_distance(x, y))
        + 4.0 * np.maximum(0.0, SETTING + BEZEL_OUT - GEM(x, y)), [0.5, 1.0])
    cut(bm, gem, [0.0, BEZEL_IN, SETTING - BEZEL_OUT, SETTING, SETTING + BEZEL_OUT])
    cut(bm, lambda x, y, z: view_of(x, y, z)[2], [OUTER, RIM])
    for _, width, span in CAUSTIC:
        cut(bm, lambda x, y, z, w=width, s=span: crescent(x, y, z, w, s), [0.0])
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    # Paint by where each face is on the undisplaced ball (the fields are the camera's view of it).
    faces = bm.faces[:]
    centres = np.array([f.calc_center_median() for f in faces])
    fx, fy, fz = centres[:, 0], centres[:, 1], centres[:, 2]
    d = petal_distance(fx, fy)
    g = GEM(fx, fy)
    _, _, rho, _ = view_of(fx, fy, fz)
    rib = rib_field(fx, fy)
    key = np.full(len(faces), "floor", dtype=object)
    on_petal = d < EDGE_OUT
    key[on_petal] = "petal"
    key[(d > -EDGE_IN) & on_petal] = "edge"
    key[(rib < 1.0) & (d > SHOULDER) & (g > SETTING + BEZEL_OUT)] = "rib"
    key[g < SETTING] = "bezel"
    key[(rho > OUTER) & on_petal & (d < -EDGE_IN)] = "outer"
    key[(crescent(fx, fy, fz, CAUSTIC[0][1], CAUSTIC[0][2]) > 0) & (d < -EDGE_IN)] = "caustic"
    key[(crescent(fx, fy, fz, CAUSTIC[1][1], CAUSTIC[1][2]) > 0) & (d < -EDGE_IN)] = "caustic_core"
    key[(rho > RIM) | (fz < 0.0)] = "rim"
    for f, kk in zip(faces, key):
        f.material_index = keys.index(kk)
    # Moved in along the radius by the height field.
    verts = bm.verts[:]
    co = np.array([v.co for v in verts])
    h = height(co[:, 0], co[:, 1]) * smoothstep(BACK_FADE, 0.0, co[:, 2])
    rho = view_of(co[:, 0], co[:, 1], co[:, 2])[2]
    h = np.where(h < 0.0, h * (1.0 - smoothstep(RIM_FADE[0], RIM_FADE[1], rho)), h)
    for v, hv in zip(verts, h.tolist()):
        rel = v.co - C
        length = rel.length
        if length > 1e-6:
            v.co = C + rel * (1.0 + hv / length)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = kit.from_bmesh("ball", bm)
    for kk in keys:
        obj.data.materials.append(mats[kk])
    k.smooth(obj, 80.0)
    kit.drop_unused_materials(obj)
    return obj


# --- The gem ---------------------------------------------------------------------------------------------------------

def gem_light(x, y):
    """The gem's brightness at view (x, y): its depth inside the outline and its two lights."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    depth = np.clip(-GEM_EXACT(x, y) / GEM_DEEP, 0.0, 1.0)
    gx, gy, gr = GEM_GLARE
    cx, cy, ca, cb = GEM_CAUSTIC
    glare = np.exp(-((x - gx) ** 2 + (y - gy) ** 2) / (2 * (gr / 2) ** 2))
    caustic = np.exp(-(((x - cx) / ca) ** 2 + ((y - cy) / cb) ** 2) * 2)
    w = GEM_WEIGHTS
    return w[0] * np.sqrt(depth) + w[1] * glare + w[2] * caustic


def gem(gem_indices, gem_glows, dark_crescent=False):
    """The cabochon in the pit, in view space: its top GEM_TOP over the ball's surface, rounded off at its edge, painted
    in bands of gem_light() (gem_indices and gem_glows: edge, middle, heart, glare, caustic); dark_crescent: blue's
    dark crescent across its lower left, in the edge's colour."""
    pal = k.level_palette()
    names = ("edge", "middle", "heart", "glare", "caustic")
    mats = {name: k.material(f"gem_{name}", palette=index, metallic=0.05, roughness=0.12, emission=pal[index],
                             emission_strength=strength)
            for name, index, strength in zip(names, gem_indices, gem_glows)}
    obj = relief("gem", GEM, GEM_TOP, mats["edge"], profile=round_profile(GEM_EDGE[0], GEM_EDGE[1], 9),
                 inner=1, spacing=0.45, base=lambda x, y: float(ball_z(x, y)), sink=1.4)
    paint(obj, lambda x, y, z: gem_light(x, y), GEM_BANDS,
          [mats["edge"], mats["middle"], mats["heart"], mats["caustic"], mats["glare"]])
    if dark_crescent:
        dark = rounded(polygon(GEM_CRESCENT), 0.45)
        paint(obj, lambda x, y, z: -dark(x, y), [0.0], [None, mats["edge"]])
    return obj


# --- Building --------------------------------------------------------------------------------------------------------

def build_model(name):
    """The model's parts in view space (the ball first)."""
    sprite, ramp, offset, gem_indices, gem_glows, has_crescent = ORBS[name]
    k.reset()
    parts = [ball(ramp, offset), gem(gem_indices, gem_glows, has_crescent)]
    for obj in parts:
        kit.drop_unused_materials(obj)
    return sprite, parts


def build():
    opts = kit.options()
    for name in ORBS:
        if not kit.wanted(opts, name):
            continue
        sprite, parts = build_model(name)
        front.triangulate(parts)
        front.check_view(opts, name, sprite, parts)
        front.to_world(parts)
        front.check_top(opts, name, sprite, parts)
        bpy.context.scene.view_settings.view_transform = "Standard"
        kit.report(name, parts, os.path.join(kit.outdir(opts), name + ".glb"))
        if "preview" in opts:
            kit.preview(opts["preview"] + name, parts, (24, 28), scale=16, distance=0.6)


if __name__ == "__main__":
    build()
