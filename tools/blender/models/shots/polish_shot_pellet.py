"""The enemy pellet (shots sheet sprites 112 and 113, 1x1: 12 x 14 cells), modelled (2026-10-29, round 2 of the energy
shots' models; until then it was drawn as its sprite with volume, flat, from the 4x sheets, with the automatic glow).

Who fires it: the commonest enemy bullet of the game. Enemy weapons 116 (37 enemy types: TYRIAN's, DELI's, GYGES',
TORM's, the asteroid levels', SURFACE's, HARVEST's, STATION's ... turrets and craft), 115, 59 and 62 (one pellet, aimed
at the player), 127 (a fan of five falling down the screen: TYRIAN's, MINES', GYGES', GAUNTLET's walkers), 145 and 146
(the asteroid levels, AST. CITY; SAVARA's and SAVARA Y's craft once fire override events give them a frequency), 68
(MARKERS, GRYPHON, CORE), 7, 8 and 6 (episodes 4 and 5: BRAINIAC, MINERS, ICE EXIT, SAVARA) and, in episode 4, 17
(SQUADRON's fighters), in episodes 1-5. An enemy's shot shows weapani frames (tyrian2.c: animate cycles below animax =
weapani, one step a game frame): every one of these weapons has weapani 2, so the pellet shows 112 and 113 by turns,
starting with 112, a flicker 35 times a second. It is round: it looks the same whichever way it flies (aimed, it flies
every way), so its lines take no yaw.

As the sprites draw it: a bead of fire 7 pixels across (columns 3-9, rows 4-10, the corner pixels cut: its middle the
middle of pixel (6, 7), half a pixel right of and below the cell's centre), the fire's ramp 7 in rings round a white
heart (0x7f at column 6 of row 7): 112 yellow-orange round it (0x7a-0x7c), red (0x75-0x77, 0x79 at its lower left),
a dark red rim (0x72) and its corners near black (0x70); 113 the same bead two or three shades hotter (a pale yellow
heart three pixels across, 0x7c-0x7f, orange 0x78-0x7a, the rim 0x73-0x74).

The model: a bead of fire round on top and flat underneath (a half-body: the game's camera only ever sees shots from
above), a dome 7 pixels across and 2.7 high, its fire in rings of ramp 7's palette indices (palette materials, so they
follow the level's palette and fades) from the yellow-orange round its heart (0x7a) out to the dark red of its rim
(0x72), by an idealized heat that falls from the heart out to the rim as the sprite's rings do; the rings' borders wave
round the bead (flames licking out from the heart, each ring's a little turned against the one inside it) and the
fire swells a little along the flames' crests, so that the game's sun puts glints on them. The mesh is built on the
rings: its rings are the bands' borders (each point at its own distance from the middle), so no face is cut (the
pulse's way). Out of its top stands the heart: a smaller dome of plasma, pale yellow in its middle and yellow round
it (0x7e, 0x7c), 0.45 pixels proud of the fire and glowing more than it (0.56-0.6: CONVENTIONS section 4). The whole
bead leans towards the camera (each point moved down the screen by 0.5 times its height): the game's camera looks
down from the bottom of the screen, 20-35 degrees off straight down, so an upright dome's top, the heart, would show a
pixel or two above its middle and its near side's dark rim wide; leant, the camera sees the rings where the sprite
lays them out, the shading still the dome's. The two frames are the same mesh: 113's materials are each band two or
three shades hotter, its heart white round pale yellow (0x7f, 0x7e) (a model per frame, as the sprite flickers). The
flat underside takes the rim's material. Every band glows in its own colour, more the hotter (0.22-0.54 the fire), so
the bead reads from the slanted camera over every ground; the glow= of its lines, a red-orange halo (0x78), makes it
pop out at once, as an enemy's bullet must, and keeps it apart from the player's own yellow pulses. 516 triangles, 7
materials (5 fire bands, 2 heart bands) each frame.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r, its top edge y = 7 - r);
the bead stands on z = 0 (the game centres shot models in height on the player's layer).

The bead's pieces (class Bead, body(), heart(), bead()) also build the enemy's yellow ball (polish_shot_eball.py) and
the minor shots' beads (polish_shot_eminor.py).

models.cfg (the shots section):
    model shot_pellet     shots/shot_pellet.glb
    model shot_pellet_113 shots/shot_pellet_113.glb
    shot shots 112 shot_pellet     glow=12:0.6:120:0.5:0.5   # the fire bead (first frame)
    shot shots 113 shot_pellet_113 glow=12:0.6:120:0.5:0.5   # two or three shades hotter (second frame)

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_pellet.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each model's top view against its sprite in
     <dir>/shots.png, from TYR3D_EXTRACT) [--preview <prefix>] (top, three-quarter and game-camera views)
"""
import math
import os
import sys

import bpy
import numpy as np

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
from polish_shot_pulse import game_view  # noqa: E402

OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")
TOP = 7.0  # the y of a 1x1 sprite's top edge

# --- The sprites (palette indices, '..' transparent) ----------------------------------------------------------------

SPRITES = {
    112: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. 70 72 72 72 70 .. .. ..
.. .. .. 70 72 75 76 75 72 70 .. ..
.. .. .. 72 76 7a 7c 7a 75 72 .. ..
.. .. .. 72 77 7b 7f 7b 76 72 .. ..
.. .. .. 72 75 79 7b 7a 75 72 .. ..
.. .. .. 70 72 75 76 75 72 70 .. ..
.. .. .. .. 70 72 72 72 70 .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    113: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. 70 73 74 73 70 .. .. ..
.. .. .. 70 73 78 79 78 73 70 .. ..
.. .. .. 73 79 7d 7e 7d 78 73 .. ..
.. .. .. 74 7a 7e 7f 7e 79 74 .. ..
.. .. .. 73 78 7c 7e 7d 78 73 .. ..
.. .. .. 70 73 78 79 78 73 70 .. ..
.. .. .. .. 70 73 74 73 70 .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
}


# --- The bead ---------------------------------------------------------------------------------------------------------
# A dome of fire round a raised heart, built on rings round its middle: its middle (x, y), its outline (a radius, or
# the radius at each angle round the middle: an outline every ray from the middle crosses once), its height (pixels;
# the dome's height at a point goes with its distance from the outline, so a long shape is as high all along its
# middle and rounds off at its ends), its heat (in the fire's shades 0-15: out from the middle, the same every way, as
# points (u, shade), u 0 the middle and 1 the outline; or a function (u, angle) -> shade, falling along every ray), its
# bands ((lowest heat, palette index, emission), coolest first; the flat underside takes the coolest's material), its
# heart (its outline the bead's scaled (sx, sy) about the middle, how far it stands proud of the fire, its bands ((from
# u, palette index, emission), the middle first)), the flames (how many round the bead, how far they reach in and out
# (u), how much each border's are turned against the one inside it (radians), how far they swell out of the surface
# (pixels)) and the points round it.


# The bead leans towards the camera (every point moved down the screen by lean times its height): the game's camera
# looks down from the bottom of the screen, 20 degrees off straight down at the bottom of the view and 35 at its top,
# so an upright dome's top would show a pixel or two above its middle and its near side's dark rim wide; leant by
# tan(26.6 degrees), the middle of that range, the camera sees the rings as the sprite lays them out (the heart in the
# middle, the rim even all round; within half a pixel anywhere on the screen), the shading still the dome's.
LEAN = 0.5


class Bead:
    def __init__(self, x, y, outline, height, heat, bands, heart, flames=(5, 0.05, 1.9, 0.1), segments=30,
                 heart_segments=12, power=2.0, head_rings=(0.45, 0.8), gap=0.25, rim_rings=(0.9, 0.965, 1.0),
                 lean=LEAN, height_fn=None, heart_rings=(0.3, 0.55, 0.75, 0.9, 1.0)):
        self.x, self.y, self.h, self.lean, self.height_fn = x, y, height, lean, height_fn
        self.heart_rings = heart_rings
        self.radius = outline if callable(outline) else (lambda a, r=float(outline): r)
        if callable(heat):
            self.heat = heat
        else:
            curve = monotone([p[0] for p in heat], [p[1] for p in heat])
            self.heat = lambda u, a: curve(u)
        self.bands, self.heart = bands, heart
        self.flames, self.segments, self.heart_segments, self.power = flames, segments, heart_segments, power
        self.head_rings, self.gap, self.rim_rings = head_rings, gap, rim_rings
        self.outline = Outline([self.point(1.0, 2 * math.pi * i / 720) for i in range(720)])
        self.deepest = max(self.outline.distance(self.point(u / 24, 2 * math.pi * i / 96))
                           for u in range(24) for i in range(96))

    def point(self, u, angle):
        r = u * self.radius(angle)
        return (self.x + r * math.cos(angle), self.y + r * math.sin(angle))

    def height_at(self, p):
        """The dome's height over a point (x, y) inside it, without the flames' swell: round, from its distance to the
        outline (or height_fn's, for shapes it suits better)."""
        if self.height_fn is not None:
            return self.height_fn(p)
        s = min(self.outline.distance(p) / self.deepest, 1.0)
        return self.h * max(0.0, 1.0 - (1.0 - s) ** self.power) ** (1.0 / self.power)


class Outline:
    """A closed polygon (points round it) and the distance of points to it."""

    def __init__(self, points):
        self.a = np.array(points, dtype=float)
        self.b = np.roll(self.a, -1, axis=0)
        self.d = self.b - self.a
        self.dd = np.maximum((self.d * self.d).sum(axis=1), 1e-12)

    def distance(self, p):
        q = np.array(p[:2], dtype=float)
        t = np.clip(((q - self.a) * self.d).sum(axis=1) / self.dd, 0.0, 1.0)
        nearest = self.a + self.d * t[:, None]
        return float(np.sqrt(((nearest - q) ** 2).sum(axis=1)).min())


def solve(f, value, lo=0.0, hi=1.0):
    """Where (u) the falling curve f first drops below value (bisection; lo if it is below already, hi if never)."""
    if f(lo) < value:
        return lo
    if f(hi) >= value:
        return hi
    for _ in range(40):
        mid = (lo + hi) / 2
        if f(mid) < value:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def border_lines(bead, angles):
    """The bands' borders round the bead, the hottest (innermost) first: u per angle, waved by the flames."""
    count, reach, turning, _ = bead.flames
    lines = []
    for n, (lowest, _, _) in enumerate(reversed(bead.bands[1:])):
        line = []
        for a in angles:
            u0 = solve(lambda u: bead.heat(u, a), lowest)
            line.append(min(max(u0 + reach * math.sin(count * a + turning * n), 0.03), 0.985))
        lines.append(line)
    for n in range(1, len(lines)):  # (each border outside the one before it at every angle)
        for j in range(len(angles)):
            lines[n][j] = max(lines[n][j], lines[n - 1][j] + 0.02)
    return lines


def ring_curves(bead, angles):
    """The body's rings as curves u(angle), from the middle out, with the band of the faces outside each and the
    flames' phase along it: the head's rings (fractions of the first border), the borders (with rings between them
    where they lie further apart than gap), the rim's rings (fixed u, so the dome rounds off to its base, the last on
    z = 0)."""
    _, _, turning, _ = bead.flames
    lines = border_lines(bead, angles)
    hottest = len(bead.bands) - 1
    curves = []
    for f in bead.head_rings:
        curves.append(([f * u for u in lines[0]], hottest, 0.0))
    for n, line in enumerate(lines):
        band = hottest - 1 - n
        curves.append((line, band, turning * n))
        following = lines[n + 1] if n + 1 < len(lines) else None
        if following is not None:
            extra = int(max(b - a for a, b in zip(line, following)) / bead.gap)
            for j in range(1, extra + 1):
                f = j / (extra + 1)
                curves.append(([a + (b - a) * f for a, b in zip(line, following)], band, turning * (n + f)))
    last = lines[-1]
    for u in bead.rim_rings:
        if u >= 1.0:
            curves.append(([1.0] * len(angles), 0, turning * (len(lines) - 1)))
        elif min(u - a for a in last) > 0.012:
            curves.append(([u] * len(angles), 0, turning * (len(lines) - 1)))
    return curves


def swell(bead, u, angle, phase):
    """How far the fire swells out of the dome at u and the angle: along the flames' crests, nothing at the middle and
    at the rim."""
    count, _, _, height = bead.flames
    return height * math.sin(count * angle + phase) * math.sin(math.pi * min(max(u, 0.0), 1.0)) ** 1.5


def dome_mesh(name, centre, rings, ring_bands, apex_band, under_band, materials, apex, smooth=70):
    """A closed mesh through rings round a vertical axis (each a closed loop of points, from the top down, the last on
    z = 0): a fan from the apex point to the first, strips between them (ring_bands[i]: the band of the faces between
    ring i and i + 1), a flat fan under the last to the middle (under_band)."""
    count = len(rings[0])
    verts = [tuple(apex)] + [tuple(p) for ring in rings for p in ring] + [(centre[0], centre[1], 0.0)]
    bottom = len(verts) - 1
    faces, mats = [], []
    for j in range(count):
        jj = (j + 1) % count
        faces.append((0, 1 + j, 1 + jj))
        mats.append(apex_band)
    for i in range(len(rings) - 1):
        a, b = 1 + i * count, 1 + (i + 1) * count
        for j in range(count):
            jj = (j + 1) % count
            faces.append((a + j, b + j, b + jj, a + jj))
            mats.append(ring_bands[i])
    base = 1 + (len(rings) - 1) * count
    for j in range(count):
        jj = (j + 1) % count
        faces.append((base + jj, base + j, bottom))
        mats.append(under_band)
    obj = k.mesh_object(name, verts, faces)
    for m in materials:
        obj.data.materials.append(m)
    for poly, m in zip(obj.data.polygons, mats):
        poly.material_index = m
    k.recalc_normals(obj)
    return k.smooth(obj, smooth)


def body(name, bead, materials):
    """The bead's fire: rings on the bands' borders round the middle, the dome's height at each point, swelling a
    little along the flames."""
    angles = [2 * math.pi * j / bead.segments for j in range(bead.segments)]
    curves = ring_curves(bead, angles)
    rings = []
    for us, _, phase in curves:
        ring = []
        for a, u in zip(angles, us):
            p = bead.point(u, a)
            z = max(0.0 if u >= 1.0 else bead.height_at(p) + swell(bead, u, a, phase), 0.0)
            ring.append((p[0], p[1] - bead.lean * z, z))
        rings.append(ring)
    bands = [c[1] for c in curves]
    top = bead.height_at((bead.x, bead.y))
    return dome_mesh(name, (bead.x, bead.y), rings, bands[:-1], len(bead.bands) - 1, 0, materials,
                     (bead.x, bead.y - bead.lean * top, top))


HEART_DIP = 0.15  # how far the heart's edge sinks into the fire (pixels)


def heart(name, bead, materials):
    """The heart: a small dome of plasma standing out of the fire's top (lift pixels at its middle), its outline the
    bead's scaled about the middle, its edge sunk into the fire; its bands out from its middle; closed under it (inside
    the fire) by a fan to z = 0."""
    sx, sy, lift, bands = bead.heart
    count = bead.heart_segments
    angles = [2 * math.pi * (j + 0.5) / count for j in range(count)]

    def at(uc, a):
        r = uc * bead.radius(a)
        return (bead.x + r * sx * math.cos(a), bead.y + r * sy * math.sin(a))
    edge = Outline([at(1.0, 2 * math.pi * i / 360) for i in range(360)])
    deepest = max(edge.distance(at(u / 12, 2 * math.pi * i / 48)) for u in range(12) for i in range(48))
    rings, ring_bands = [], []
    for uc in bead.heart_rings:
        ring = []
        for a in angles:
            p = at(uc, a)
            s = min(edge.distance(p) / deepest, 1.0)
            z = bead.height_at(p) + lift * math.sqrt(max(0.0, 2 * s - s * s)) - HEART_DIP * uc * uc
            ring.append((p[0], p[1] - bead.lean * z, z))
        rings.append(ring)
        ring_bands.append(max(i for i, b in enumerate(bands) if uc >= b[0] - 1e-9))
    # (the strips take the band of their inner ring; the last ring's skirt down to z = 0 inside the fire)
    rings.append([(p[0], p[1] + bead.lean * p[2], 0.0) for p in rings[-1]])
    ring_bands.append(len(bands) - 1)
    top = bead.height_at((bead.x, bead.y)) + lift
    return dome_mesh(name, (bead.x, bead.y), rings, ring_bands[:-1], 0, len(bands) - 1, materials,
                     (bead.x, bead.y - bead.lean * top, top), smooth=80)


def bead(name, spec, fire, heart_mats):
    """The bead's two meshes: its fire and its heart."""
    parts = [body(name + "_fire", spec, fire)]
    if spec.heart is not None:
        parts.append(heart(name + "_heart", spec, heart_mats))
    return parts


def materials(prefix, bands, roughness):
    return [lit(f"{prefix}_{index:02x}", index, glow, roughness=roughness) for _, index, glow in bands]


# --- The pellet -------------------------------------------------------------------------------------------------------
# The heat out from the middle (u = r / 3.5): the sprite's rings (its heart 15, the pixels round it 11-12, then 9-10,
# the red ring 5-7, the rim 2, its corners 0).
HEAT = ((0.0, 15.0), (0.2, 13.2), (0.3, 11.5), (0.43, 9.4), (0.57, 6.6), (0.71, 4.1), (0.86, 2.0), (1.0, 0.8))
RADIUS, HEIGHT = 3.5, 2.7
# Its fire's bands in each frame ((lowest heat, palette index, emission), the rim first) and its heart's ((from u,
# index, emission), the middle first): 113 two or three shades hotter on the same borders.
BANDS = {
    112: [(-99.0, 0x72, 0.22), (2.6, 0x74, 0.28), (4.2, 0x76, 0.35), (6.0, 0x78, 0.42), (8.0, 0x7a, 0.48)],
    113: [(-99.0, 0x73, 0.24), (2.6, 0x76, 0.34), (4.2, 0x78, 0.42), (6.0, 0x7a, 0.48), (8.0, 0x7c, 0.54)],
}
HEART_BANDS = {
    112: ((0.0, 0x7e, 0.6), (0.55, 0x7c, 0.56)),
    113: ((0.0, 0x7f, 0.6), (0.55, 0x7e, 0.6)),
}
HEART = (1.8, 0.45)  # (radius, how far it stands proud of the fire)
FIRE_ROUGHNESS, HEART_ROUGHNESS = 0.5, 0.4


def pellet_bead(frame):
    size = HEART[0] / RADIUS
    return Bead(0.5, -0.5, RADIUS, HEIGHT, HEAT, BANDS[frame], (size, size, HEART[1], HEART_BANDS[frame]), segments=26,
                heart_segments=10, head_rings=(0.5,), heart_rings=(0.35, 0.65, 0.88, 1.0))


# name: (sprite, what it is)
MODELS = [
    ("shot_pellet", 112, "the fire bead (the first frame)"),
    ("shot_pellet_113", 113, "the fire bead two or three shades hotter (the second frame)"),
]


def build_model(name, sprite):
    spec = pellet_bead(sprite)
    fire = materials("pellet_fire", spec.bands, FIRE_ROUGHNESS)
    hearts = materials("pellet_heart", spec.heart[3], HEART_ROUGHNESS)
    return triangulate(bead(name, spec, fire, hearts))


def run(models, build_one, default_outdir=OUTDIR, sheet="shots.png"):
    """The scripts' common main: builds each (name, sprite, what, ...) of models with build_one(name, sprite, ...)
    -> parts, with --only, --outdir, --check and --preview."""
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", default_outdir)
    for entry in models:
        name, sprite, what = entry[0], entry[1], entry[2]
        if only is not None and name not in only:
            continue
        k.reset()
        parts = build_one(*entry[:2], *entry[3:])
        bpy.context.view_layer.update()
        print(f"== {name} (shots {sprite}): {what}")
        if "check" in options:
            check_frames(parts, os.path.join(options["check"], sheet), [(sprite, turn(0), f"shots {sprite}")],
                         move_to_frame=False)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            game_view(options["preview"] + name, parts)


if __name__ == "__main__":
    run(MODELS, build_model)
