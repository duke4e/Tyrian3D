"""The Starburst's shots (shots sheet sprites 172-181, all 1x1: 12 x 14 cells), modelled (2026-10-29, round 2 of the
energy shots' models; until then they were drawn as their sprites with volume, flat, with the automatic glow).

Who fires them: the Starburst (rear weapon port 9, weapons 243-253 for power levels 1-11): stars flying out round the
ship, 10-12 pixels a game frame, each living 10 frames (del 10), in 6 directions at power 1, 3, 5, 7, 9 and 10
((-10, 4), (10, -4), (-10, -4), (10, 4), (-12, 0), (12, 0)) or 8 at power 2, 4, 6, 8 and 11 ((+-9, +-6), (+-10, +-3)),
taking turns: one star every 3 frames at power 1-2, every 2 at 3-4, two at a time at 5-8 (every 3 frames, then 2), four
at 9, all six at once every 4 frames at 10 and all eight every 3 at 11; also the second player's rear port 9 in
two-player games (the linked turret, weapon 444, and the charge cannon, weapons 476-481). A player's shot shows weapani
+ 1 frames (shots.c shotAniMax): all ten, 172 to 181, one a frame, so each star shrinks and fades as it flies out.
Enemies never fire them: weapons 251-255 in an enemy's turret are special cases of tyrian2.c's firing switch (252
"Savara Boss DualMissile" sets up two explosions, 251 and 253-255 are magnets), so the records' sprites (252 and 253:
172 in rings of 6 and 8) are never shot.

As the sprites draw them: a four-pointed star of the fire's ramp 7, its middle at column 5, row 6 of the cell (half a
pixel left of and above the cell's centre), the frames alternating a + (172, 174, 176, 178, 180: arms along the screen's
axes) and an x (173 ... 181: the same star turned 45 degrees, its diagonal arms reaching a little further). Each arm
is hot down its middle and dark at its edges (172's: 0x7e in the middle, 0x7c 0x7a 0x78 0x77 0x76 down each arm to a
dark red tip, 0x71 0x74 0x76 0x79 at its sides), so the colours lie in stars inside stars. The frames shrink and darken
in pairs: 172/173 large (arms 5.5-6.5 pixels; the x's 7), 174-179 medium (4.5-5.5; the x's 5.7) and two shades darker
each pair (the middle 0x7c, 0x7a, 0x78), 180/181 small (3; the middle 0x77, 0x74).

The model: one star, raised and glowing, flat underneath (a half-body: the game's camera only sees it from above), its
four arms 4.3 pixels wide at the middle and tapering (a little full) to sharp tips 6 pixels out, each arm's section a
rounded ridge (a superellipse a little sharper than an ellipse), the arms' sides meeting in creased notches between
them. A little bolder than the sprite's thin cross (its arms a hot pixel between dark ones): with the arms' width of
the sprite's dark edges it read thin and dark next to the HD volumes' fat orange diamonds at 1x. Its fire is in
bands of ramp 7 by an idealized heat (hottest in the middle, cooling along each arm and faster towards its sides:
ALONG and ACROSS, as the sprite's middle columns and edges go), and the mesh is built on the bands: a polar mesh whose
rings are the bands' borders (star-shaped closed curves round the middle, each point on its spoke where the heat falls
below the border), with rings between only where they lie far apart, so no face is cut along a border (the pulse's
method). In the middle a core of plasma stands out of the fire: a smaller four-pointed star, pale yellow in its middle
and yellow along its short arms (the sprite's hot middle and the hot lines down its arms, raised). 7 materials: 5 bands
of the fire (0x75 at the tips and edges, 0x77, 0x79, 0x7b, 0x7c round the core) and 2 of the core (0x7e, 0x7d), each
glowing in its own colour by its shade (0.31-0.6); 856 triangles.

The frames: one mesh for all ten (models.cfg turns it 45 degrees for the x frames, yaw=45, and sizes it with scale=,
at=-0.5:-0.5 putting its middle on the sprite's). What changes from pair to pair is the brightness: a model per pair,
the same mesh with every band's palette index (and so its glow) two shades lower each pair: shot_starburst (172 173),
shot_starburst_174 (174 175, two shades lower), _176 (four), _178 (six), _180 (180 181, eight; the darkest band stops
at 0x70, the ramp's end: 6 materials).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
star's middle (models.cfg's at= moves it onto the sprite's: column 5, row 6 of the cell, half a pixel left of and above
the cell's centre); the star stands on z = 0 (the game centres shot models in height on the player's layer).

models.cfg (the shots section; at= puts the star's middle on the sprite's, glow= round it, fading with the frames):
    model shot_starburst     shots/shot_starburst.glb
    model shot_starburst_174 shots/shot_starburst_174.glb
    model shot_starburst_176 shots/shot_starburst_176.glb
    model shot_starburst_178 shots/shot_starburst_178.glb
    model shot_starburst_180 shots/shot_starburst_180.glb
    shot shots 172 shot_starburst     at=-0.5:-0.5                   glow=14:0.55:124:-0.5:-0.5
    shot shots 173 shot_starburst     at=-0.5:-0.5 yaw=45 scale=1.16 glow=15:0.55:124:-0.5:-0.5
    shot shots 174 shot_starburst_174 at=-0.5:-0.5        scale=0.84 glow=12:0.5:123:-0.5:-0.5
    shot shots 175 shot_starburst_174 at=-0.5:-0.5 yaw=45 scale=0.96 glow=13:0.5:123:-0.5:-0.5
    shot shots 176 shot_starburst_176 at=-0.5:-0.5        scale=0.84 glow=11:0.45:121:-0.5:-0.5
    shot shots 177 shot_starburst_176 at=-0.5:-0.5 yaw=45 scale=0.96 glow=12:0.45:121:-0.5:-0.5
    shot shots 178 shot_starburst_178 at=-0.5:-0.5        scale=0.84 glow=10:0.38:120:-0.5:-0.5
    shot shots 179 shot_starburst_178 at=-0.5:-0.5 yaw=45 scale=0.96 glow=11:0.38:120:-0.5:-0.5
    shot shots 180 shot_starburst_180 at=-0.5:-0.5        scale=0.58 glow=8:0.3:119:-0.5:-0.5
    shot shots 181 shot_starburst_180 at=-0.5:-0.5 yaw=45 scale=0.52 glow=8:0.3:119:-0.5:-0.5

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_starburst.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each frame's top view against its sprite
     in <dir>/shots.png, from TYR3D_EXTRACT) [--preview <prefix>] (top, three-quarter and game-camera views, and
     <prefix>frames_game.png and frames_top.png: the ten frames as models.cfg shows them)
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ENEMIES = os.path.join(HERE, "..", "enemies")
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, ENEMIES)
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_flame_drop import monotone  # noqa: E402
from polish_launched_flames import lit, check_frames, turn  # noqa: E402

OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")

# --- The sprites (palette indices, '..' transparent; for reference and the docstring's measurements) -----------------

SPRITES = {
    172: """
.. .. .. .. .. 71 .. .. .. .. .. ..
.. .. .. .. .. 76 .. .. .. .. .. ..
.. .. .. .. 71 77 71 .. .. .. .. ..
.. .. .. .. 74 78 74 .. .. .. .. ..
.. .. .. .. 76 7a 76 .. .. .. .. ..
.. .. 71 74 79 7c 79 74 71 .. .. ..
71 76 78 7a 7c 7e 7c 7a 78 76 71 ..
.. .. 71 74 79 7c 79 74 71 .. .. ..
.. .. .. .. 76 7a 76 .. .. .. .. ..
.. .. .. .. 74 78 74 .. .. .. .. ..
.. .. .. .. 71 77 71 .. .. .. .. ..
.. .. .. .. .. 75 .. .. .. .. .. ..
.. .. .. .. .. 71 .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    173: """
.. .. .. .. .. .. .. .. .. .. .. ..
71 .. .. .. .. .. .. .. .. .. 71 ..
.. 76 71 .. .. .. .. .. 71 76 .. ..
.. 71 78 76 .. .. .. 76 78 71 .. ..
.. .. 76 7a 78 72 78 7a 76 .. .. ..
.. .. .. 78 7c 7a 7c 78 .. .. .. ..
.. .. .. 72 7a 7e 7a 72 .. .. .. ..
.. .. .. 78 7c 7a 7c 78 .. .. .. ..
.. .. 76 7a 78 72 78 7a 76 .. .. ..
.. 71 78 76 .. .. .. 76 78 71 .. ..
.. 76 71 .. .. .. .. .. 71 76 .. ..
71 .. .. .. .. .. .. .. .. .. 71 ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    174: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. 74 .. .. .. .. .. ..
.. .. .. .. .. 75 .. .. .. .. .. ..
.. .. .. .. 72 76 72 .. .. .. .. ..
.. .. .. .. 74 78 74 .. .. .. .. ..
.. .. .. 72 77 7a 77 72 .. .. .. ..
.. 74 76 78 7a 7c 7a 78 76 74 .. ..
.. .. .. 72 77 7a 77 72 .. .. .. ..
.. .. .. .. 74 78 74 .. .. .. .. ..
.. .. .. .. 72 76 72 .. .. .. .. ..
.. .. .. .. .. 75 .. .. .. .. .. ..
.. .. .. .. .. 73 .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    180: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. 70 .. .. .. .. .. ..
.. .. .. .. .. 72 .. .. .. .. .. ..
.. .. .. .. 71 74 71 .. .. .. .. ..
.. .. 70 72 74 77 74 72 70 .. .. ..
.. .. .. .. 71 74 71 .. .. .. .. ..
.. .. .. .. .. 72 .. .. .. .. .. ..
.. .. .. .. .. 70 .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
}

# --- The star ---------------------------------------------------------------------------------------------------------
# A four-pointed star in the plane, its arms along +-x and +-y: each arm's half-width w(d) at d pixels from the middle
# tapers from W0 to 0 at the tip (TIP pixels out), as (1 - d / TIP) ** TAPER (1: straight, the sides concave between
# the arms); the arms' sides meet in notches on the diagonals. Its top over a point: the nearer arm's section, a
# superellipse (power SECTION: 2 an ellipse, less a sharper ridge) DEPTH times the arm's half-width high at its middle
# line, so the middle lines are ridges falling straight to the tips.


class Star:
    def __init__(self, tip, w0, taper=1.0, depth=0.9, section=1.7):
        self.tip, self.w0, self.taper, self.depth, self.section = tip, w0, taper, depth, section

    def width(self, d):
        """The arm's half-width d pixels from the middle."""
        f = max(0.0, 1.0 - d / self.tip)
        return self.w0 * f ** self.taper

    def local(self, x, y):
        """(d, a): along the nearer arm and across it (both >= 0)."""
        ax, ay = abs(x), abs(y)
        return (ax, ay) if ax >= ay else (ay, ax)

    def across(self, x, y):
        """How far out across the nearer arm (0 its middle line, 1 its edge)."""
        d, a = self.local(x, y)
        w = self.width(d)
        return a / w if w > 1e-9 else 2.0

    def height(self, x, y):
        """The star's top over (x, y), 0 outside it."""
        d, a = self.local(x, y)
        w = self.width(d)
        if w <= 1e-9 or a >= w:
            return 0.0
        u = a / w
        return self.depth * w * (1.0 - u ** self.section) ** (1.0 / self.section)

    def outline(self, phi):
        """The radius of the star's edge on the spoke at angle phi (radians, 0 along +x)."""
        lo, hi = 0.0, self.tip * 1.0001
        for _ in range(50):
            mid = (lo + hi) / 2
            if self.across(mid * math.cos(phi), mid * math.sin(phi)) < 1.0:
                lo = mid
            else:
                hi = mid
        return lo


BODY = Star(tip=6.0, w0=2.15, taper=0.9, depth=0.85, section=1.8)
# The spokes of the polar mesh, in degrees from an arm's middle line to the notch (45): close at the tips (sharp) and
# at the notches (where the borders crowd); mirrored into the eight half-arms.
SPOKES = (0.0, 2.5, 7.0, 15.0, 27.0, 45.0)
# The fire's heat (in shades of ramp 7): along an arm's middle line (t: 0 the star's middle, 1 the tip; the sprite's
# 0x7e, 0x7c, 0x7a, 0x78, 0x77, 0x76 ... down 172's arms), minus ACROSS(t) times the square of the way out to its edge
# (the sprite's arm edges are 3-6 shades darker than its middle line), so the colours lie in stars inside stars.
ALONG = ((0.0, 14.5), (0.15, 13.2), (0.35, 11.2), (0.55, 9.2), (0.72, 7.6), (0.87, 6.0), (1.0, 4.4))
ACROSS = ((0.0, 4.0), (0.2, 5.0), (0.5, 5.0), (0.8, 3.6), (1.0, 2.0))
# The fire's bands: (lowest heat, palette index) of ramp 7, the tips' and edges' dark red to the yellow round the core;
# each glows in its own colour by its shade (glow_of). The flat underside, never seen, takes the darkest band.
BODY_BANDS = ((-99.0, 0x75), (5.2, 0x77), (7.0, 0x79), (8.8, 0x7b), (10.8, 0x7c))
FIRE_ROUGHNESS = 0.5
# Rings between the borders: a ring between two borders further apart than GAP (pixels, on any spoke), INNER rings
# between the middle and the first border (fractions of the way), one between the last border and the edge (TAIL).
GAP = 1.15
INNER = (0.45,)
TAIL = (0.5,)

# The core: a smaller star standing LIFT pixels out of the fire's top at its middle (less towards its tips), its own
# bands by its own heat (1 in its middle, 0 at its edge): pale yellow in the middle, yellow along its arms.
CORE = Star(tip=3.0, w0=0.85, taper=1.0, depth=1.0, section=1.8)
CORE_LIFT = 0.42
CORE_SPOKES = (0.0, 8.0, 22.0, 45.0)
CORE_RINGS = (0.22, 0.42, 0.68, 0.88, 1.0)  # fractions of the way to the core's edge on each spoke
CORE_SINK = 0.08  # its edge this far under the fire's top
CORE_BANDS = ((0.0, 0x7e), (0.42, 0x7d))  # (from the fraction of the way out, palette index)
CORE_ROUGHNESS = 0.4

# The frames: a model per brightness (every band two shades lower each pair); the + frames as built, the x frames
# turned 45 degrees; scale: the frame's size against 172's (its arms' reach: 172's 5.5-6.5 pixels; the x frames'
# 7 (173), 5.7 (175 177 179), 2.8 (181)); at: the star's middle on the sprite's (column 5, row 6).
MODELS = [  # (name, shades darker, sprites)
    ("shot_starburst", 0, (172, 173)),
    ("shot_starburst_174", 2, (174, 175)),
    ("shot_starburst_176", 4, (176, 177)),
    ("shot_starburst_178", 6, (178, 179)),
    ("shot_starburst_180", 8, (180, 181)),
]
FRAMES = {  # sprite: (yaw, scale)
    172: (0.0, 1.0), 173: (45.0, 1.16),
    174: (0.0, 0.84), 175: (45.0, 0.96),
    176: (0.0, 0.84), 177: (45.0, 0.96),
    178: (0.0, 0.84), 179: (45.0, 0.96),
    180: (0.0, 0.58), 181: (45.0, 0.52),
}
AT = (-0.5, -0.5)  # (dx, dy down the screen): the sprite's middle against the cell's centre


def glow_of(shade):
    """Emission strength by palette shade (CONVENTIONS 4: 0.2-0.28 dark red, 0.31-0.42 red and orange, 0.46-0.54
    orange-yellow, 0.56-0.62 the cores)."""
    if shade <= 11:
        return round(max(0.12, 0.135 + 0.0355 * shade), 3)
    return round(min(0.62, 0.56 + 0.02 * (shade - 12)), 3)


def darker(index, shades):
    """The palette index that many shades lower in its ramp (not below the ramp's first)."""
    return (index & 0xF0) | max(0, (index & 15) - shades)


# --- Building ---------------------------------------------------------------------------------------------------------

_along = monotone([p[0] for p in ALONG], [p[1] for p in ALONG])
_across = monotone([p[0] for p in ACROSS], [p[1] for p in ACROSS])


def heat(x, y):
    d, a = BODY.local(x, y)
    t = min(d / BODY.tip, 1.0)
    u = min(BODY.across(x, y), 1.3)
    return _along(t) - _across(t) * u * u


def spoke_angles(spokes):
    """Every spoke round the star (radians, counter-clockwise from +x), from the half-arm's angles."""
    half = [math.radians(s) for s in spokes]
    one = [-a for a in reversed(half[1:])] + half[:-1]  # (-45, 45] of an arm, the notch at -45 shared with the last
    return [q * math.pi / 2 + a for q in range(4) for a in one]


def border_on(phi, value, edge, steps=240):
    """Where on the spoke at phi (radius) the heat first falls below value; the edge if it doesn't."""
    c, s = math.cos(phi), math.sin(phi)
    previous = 0.0
    for i in range(1, steps + 1):
        r = edge * i / steps
        if heat(r * c, r * s) < value:
            lo, hi = previous, r
            for _ in range(40):
                mid = (lo + hi) / 2
                if heat(mid * c, mid * s) < value:
                    hi = mid
                else:
                    lo = mid
            return (lo + hi) / 2
        previous = r
    return edge


def body_rings(phis, edges):
    """The rings of the fire's mesh, middle to edge, as radii per spoke, and the band of the faces outside each:
    [(radii, band)], the last the star's edge."""
    borders = [[border_on(p, lowest, e) for p, e in zip(phis, edges)] for lowest, _ in reversed(BODY_BANDS[1:])]
    # (each border outside the one before on every spoke, and inside the edge)
    for k in range(len(borders)):
        for j, e in enumerate(edges):
            low = borders[k - 1][j] + 0.02 if k > 0 else 0.05
            borders[k][j] = min(max(borders[k][j], low), e - 0.02 * (len(borders) - k))
    hottest = len(BODY_BANDS) - 1
    rings = [([f * r for r in borders[0]], hottest) for f in INNER]
    for i, line in enumerate(borders):
        band = hottest - 1 - i
        rings.append((line, band))
        following = borders[i + 1] if i + 1 < len(borders) else None
        if following is not None:
            gap = max(b - a for a, b in zip(line, following))
            extra = int(gap / GAP)
            for j in range(1, extra + 1):
                f = j / (extra + 1)
                rings.append(([a + (b - a) * f for a, b in zip(line, following)], band))
    last = borders[-1]
    for f in TAIL:
        rings.append(([a + (e - a) * f for a, e in zip(last, edges)], 0))
    rings.append((list(edges), 0))
    return rings


def polar_mesh(name, phis, rings, centre_band, top, materials, under=None):
    """A mesh over closed rings round the middle: rings [(radii per spoke, band of the faces outside it)], the middle
    vertex (top(0, 0)) fanned to the first ring (centre_band), z = top(x, y) at every vertex; under: the band of a flat
    underside under the last ring (the star's edge, at z = 0), or None (open: a core inside the fire, its faces wound
    upwards as built). materials: one per band (bands sharing a material share its slot)."""
    count = len(phis)
    verts = [(0.0, 0.0, top(0.0, 0.0))]
    for radii, _ in rings:
        for phi, r in zip(phis, radii):
            x, y = r * math.cos(phi), r * math.sin(phi)
            verts.append((x, y, top(x, y)))
    faces, bands = [], []
    for j in range(count):
        jj = (j + 1) % count
        faces.append((0, 1 + j, 1 + jj))
        bands.append(centre_band)
    for i in range(len(rings) - 1):
        a0, b0 = 1 + i * count, 1 + (i + 1) * count
        band = rings[i][1]
        for j in range(count):
            jj = (j + 1) % count
            faces.append((a0 + j, b0 + j, b0 + jj, a0 + jj))
            bands.append(band)
    if under is not None:
        bottom = len(verts)
        verts.append((0.0, 0.0, 0.0))
        last = 1 + (len(rings) - 1) * count
        for j in range(count):
            jj = (j + 1) % count
            faces.append((bottom, last + jj, last + j))
            bands.append(under)
    obj = k.mesh_object(name, verts, faces)
    slots = []
    for m in materials:
        if m not in slots:
            slots.append(m)
            obj.data.materials.append(m)
    for poly, band in zip(obj.data.polygons, bands):
        poly.material_index = slots.index(materials[band])
    if under is not None:
        k.recalc_normals(obj)
    return obj


def fire(name, materials):
    phis = spoke_angles(SPOKES)
    edges = [BODY.outline(p) for p in phis]
    rings = body_rings(phis, edges)
    # (the edge ring exactly on z = 0, the rest on the star's top)
    def top(x, y):
        return BODY.height(x, y)
    obj = polar_mesh(name, phis, rings, len(BODY_BANDS) - 1, top, materials, under=0)
    return k.smooth(obj, 75)


def core(name, materials):
    """The core: a small star standing out of the fire's top in the middle, its edge sunk a little into the fire."""
    phis = spoke_angles(CORE_SPOKES)
    edges = [CORE.outline(p) for p in phis]
    rings = []
    for f in CORE_RINGS:  # (each ring's outside faces: the band its fraction lies in)
        band = max(i for i, b in enumerate(CORE_BANDS) if f >= b[0] - 1e-9)
        rings.append(([f * e for e in edges], band))

    def top(x, y):
        rise = 1.0 if abs(x) < 1e-9 and abs(y) < 1e-9 else CORE.height(x, y) / (CORE.depth * CORE.w0)
        return BODY.height(x, y) + CORE_LIFT * rise - (CORE_SINK if rise < 1e-6 else 0.0)
    obj = polar_mesh(name, phis, rings, 0, top, materials)
    return k.smooth(obj, 80)


def build_model(name, shades):
    """The star with every band `shades` darker."""
    body_mats = []
    for _, index in BODY_BANDS:
        i = darker(index, shades)
        body_mats.append(lit(f"starburst_fire_{i:02x}", i, glow_of(i & 15), roughness=FIRE_ROUGHNESS))
    core_mats = []
    for _, index in CORE_BANDS:
        i = darker(index, shades)
        core_mats.append(lit(f"starburst_core_{i:02x}", i, glow_of(i & 15), roughness=CORE_ROUGHNESS))
    parts = [fire(f"{name}_fire", body_mats), core(f"{name}_core", core_mats)]
    return triangulate(parts)


def frame_matrix(sprite):
    """The model as models.cfg shows it in the sprite's cell: turned, sized and moved onto the sprite's middle."""
    yaw, scale = FRAMES[sprite]
    return Matrix.Translation((AT[0], -AT[1], 0.0)) @ turn(yaw) @ Matrix.Scale(scale, 4)


# --- Previews ---------------------------------------------------------------------------------------------------------

def game_camera(scene, ortho, size):
    data = bpy.data.cameras.new("game")
    data.type = "ORTHO"
    data.ortho_scale = ortho
    cam = bpy.data.objects.new("game", data)
    tilt = math.radians(20.0)
    cam.location = (0.0, -60.0 * math.sin(tilt), 60.0 * math.cos(tilt))
    cam.rotation_euler = (tilt, 0.0, 0.0)
    scene.collection.objects.link(cam)
    sun = bpy.data.lights.new("game_sun", "SUN")
    sun.energy = 3.0
    sun_obj = bpy.data.objects.new("game_sun", sun)
    sun_obj.rotation_euler = Vector((0.6, -0.6, -1.0)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sun_obj)
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = size
    return cam, sun_obj


def game_view(prefix, objects):
    """The model as the game's camera sees it (20 degrees from straight down, from the bottom of the screen), lit by the
    game's sun, with a three-quarter view (mk.preview's top and three-quarter views first)."""
    mk.preview(prefix, objects, size=(12, 14), scale=32, distance=0.42)
    scene = bpy.context.scene
    cam, sun = game_camera(scene, 16.0, (512, 512))
    scene.render.filepath = prefix + "_game.png"
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
    bpy.data.objects.remove(sun)


def frames_view(prefix):
    """The ten frames side by side as models.cfg shows them (turned, sized and moved; the game camera)."""
    k.reset()
    scene = bpy.context.scene
    scene.view_settings.view_transform = "Standard"
    objects = []
    for n, sprite in enumerate(range(172, 182)):
        name, shades, _ = next(m for m in MODELS if sprite in m[2])
        parts = build_model(f"{name}_{sprite}", shades)
        mk.transform(parts, Matrix.Translation(((n - 4.5) * 13.0, 0.0, 0.0)) @ frame_matrix(sprite))
        objects += parts
    bpy.context.view_layer.update()
    cam, sun = game_camera(scene, 134.0, (1600, 240))
    scene.render.filepath = prefix + "frames_game.png"
    bpy.ops.render.render(write_still=True)
    # (and from straight above, the cells side by side 13 pixels apart: to set against the sprites)
    cam.rotation_euler = (0.0, 0.0, 0.0)
    cam.location = (0.0, 0.0, 60.0)
    scene.render.filepath = prefix + "frames_top.png"
    bpy.ops.render.render(write_still=True)


OUTPUT = OUTDIR


def build():
    global OUTPUT
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    OUTPUT = options.get("outdir", OUTDIR)
    for name, shades, sprites in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts = build_model(name, shades)
        bpy.context.view_layer.update()
        print(f"== {name} (shots {', '.join(str(s) for s in sprites)}): the star, {shades} shades darker")
        if "check" in options:
            check_frames(parts, os.path.join(options["check"], "shots.png"),
                         [(s, frame_matrix(s), f"shots {s}") for s in sprites], move_to_frame=False)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(OUTPUT, name + ".glb"))
        if "preview" in options:
            game_view(options["preview"] + name, parts)
    if "preview" in options and only is None:
        frames_view(options["preview"])


if __name__ == "__main__":
    build()
