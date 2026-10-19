"""The round lump of molten rock (1x1: an 11 x 13 ball in the 12 x 14 cell), polished (2026-10-19; it replaces
wave2_h.py's ball of crust plates). The same pixels are two enemies' sprites: CORE's orange rune orb (sheet 3
sprite 134; enemy 259, which launches 258, and 255 and 258, which flicker between 134 and 135) and TIME WAR's
and SQUADRON's lava ball (sheet L 115, one frame). models.cfg: sprite 3 134 molten_rock, sprite l 115
molten_rock, frame 3 135 molten_rock_135.

As the sprites and their 4x upscales draw it: a glassy ball of molten rock, red-hot (the sprite's 74-77),
darker towards its rim (its outline 70-72), with patches of cooler dark crust (71-73) in the hollows between
the strokes of a glowing rune, orange to yellow (78-7d): a bar across the top from the white-hot spot at the
upper left (7d) to the right, a leg down the left side, a leg down the middle and a curve down the right. Its
frame 135 is the same picture two shades hotter everywhere (each index + 2): the frame model molten_rock_135 is
the same ball in those shades, glowing brighter (no other enemy shows sheet 3's 135).

The ball: an icosphere, finer on the side the game's camera sees, made lumpy with smooth noise; the crust
patches raised a little as plates with cracks between them, the rune's strokes sunk as glowing channels, the
hot spot swelling out. The heat painted on it is cut into bands of the sprite's own palette indices (ramp 7),
the hot bands glowing in their own colour (polish_orb_red.band_split).

Origin at the sprite's centre (pixel 6, 7), the ball standing on z = 0; +Y up the sprite, +Z towards the camera.
The game centres the ball in height on its layer (models.cfg has no origin for it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette
against enemy_3.png's 134), --preview <prefix> (top and 3/4 views of each frame).
"""
import math
import os
import random
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_sphere_nozzle import arc, fibonacci_points, smoothstep  # noqa: E402

CENTRE = Vector((-0.5, -0.5, 0.0))  # the sprite's columns 0-10, rows 1-13
RADII = Vector((5.45, 6.4, 5.2))
MEAN_RADIUS = 5.7
SEED = 134


def P(c, r):
    """A pixel's centre (column c, row r) of the 12 x 14 cell."""
    return Vector((c + 0.5 - 6.0, 7.0 - (r + 0.5)))


# The rune's strokes as the sprite draws them (pixel centres, smoothed): the bar across the top, the legs.
STROKES = [
    [P(2.2, 4.6), P(3.4, 4.9), P(4.6, 4.4), P(5.6, 3.7), P(6.8, 3.8), P(7.8, 4.3)],  # the bar over the top
    [P(2.4, 4.8), P(1.9, 6.4), P(1.8, 7.8), P(2.1, 9.2), P(2.4, 10.0)],            # the left leg
    [P(4.6, 5.8), P(5.1, 7.0), P(5.2, 8.2), P(5.5, 9.4), P(6.0, 10.4)],            # the middle leg
    [P(6.6, 5.2), P(7.4, 6.0), P(8.4, 6.9), P(9.0, 8.0)],                          # the curve down the right
]
STROKE_HALF_WIDTH = 0.62
HOT_SPOT = (P(3.4, 5.0), 1.05)  # the white-hot spot at the upper left: centre, radius
# The cooler crust in the hollows between the strokes (the sprite's 70-73): centre, radius, how cool.
CRUST = [(P(3.5, 7.8), 1.1, 1.0), (P(4.0, 9.4), 0.8, 0.8), (P(7.3, 8.4), 1.5, 1.0), (P(8.2, 5.8), 0.7, 0.7),
         (P(5.4, 1.8), 0.9, 0.6), (P(2.4, 11.6), 0.9, 0.6), (P(9.4, 4.0), 0.7, 0.5)]
CELLS = 26

# The heat bands of frame 134: (lowest heat, palette index, emission strength in the palette colour). Frame
# 135's are each two shades hotter.
BANDS = [
    (-9.0, 0x70, 0.0),
    (0.10, 0x71, 0.0),
    (0.18, 0x72, 0.06),
    (0.26, 0x73, 0.18),
    (0.34, 0x74, 0.32),
    (0.42, 0x75, 0.45),
    (0.50, 0x76, 0.6),
    (0.58, 0x77, 0.75),
    (0.66, 0x78, 0.9),
    (0.74, 0x79, 1.1),
    (0.82, 0x7a, 1.3),
    (0.90, 0x7b, 1.5),
    (0.98, 0x7c, 1.75),
    (1.06, 0x7d, 2.0),
    (1.16, 0x7e, 2.4),
]
FRAMES = [("molten_rock", 134, 0), ("molten_rock_135", 135, 2)]


def segment_distance(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.dot(ab), 1e-9)))
    return (a + ab * t - p).length


STROKE_PATHS = [mk.chaikin([tuple(q) for q in s], 2, closed=False) for s in STROKES]


def stroke_distance(p):
    best = 1e9
    for path in STROKE_PATHS:
        for a, b in zip(path, path[1:]):
            best = min(best, segment_distance(p, Vector(a), Vector(b)))
    return best


class Crust:
    """Plates of the crust: Voronoi cells of points on the ball, the cracks between them."""

    def __init__(self):
        rng = random.Random(SEED)
        self.seeds = fibonacci_points(CELLS, rng, jitter=0.7)
        self.weights = [rng.uniform(0.0, 0.1) for _ in self.seeds]
        self.lift = [rng.uniform(0.6, 1.0) for _ in self.seeds]

    def edge(self, d):
        """The nearest plate and the distance to its edge (pixels) for the direction d."""
        near = sorted((arc(d, s) - w, i) for i, (s, w) in enumerate(zip(self.seeds, self.weights)))[:2]
        return near[0][1], (near[1][0] - near[0][0]) / 2 * MEAN_RADIUS


def heat_and_lift(crust, point, d):
    """The heat (0: the dark rim, about 0.45 red-hot, 1 and more white-hot) at a point of the ball whose
    direction from its middle is d, and how far the surface is raised there."""
    xy = point.to_2d()
    lift = 0.32 * noise.noise(d * 1.5 + Vector((3.0, 7.0, 1.0))) + 0.12 * noise.noise(d * 4.0 + Vector((9.0, 2.0, 5.0)))
    heat = 0.53 + 0.08 * noise.noise(d * 2.4 + Vector((1.0, 5.0, 2.0))) + 0.05 * noise.noise(d * 6.0)
    seen = smoothstep(-0.1, 0.35, d.z)  # the strokes and patches as the camera sees the ball, from above
    # The cooler crust in the hollows: raised plates with hot cracks between them.
    cool = 0.0
    for centre, radius, amount in CRUST:
        r = (xy - centre).length
        cool = max(cool, amount * smoothstep(radius * 1.25, radius * 0.45, r))
    cool *= seen
    plate, edge = crust.edge(d)
    inside = smoothstep(0.05, 0.6, edge)
    heat -= 0.36 * cool * inside
    heat += 0.1 * cool * (1 - inside)
    lift += 0.26 * cool * inside * crust.lift[plate] - 0.1 * cool * (1 - inside)
    # The rune's strokes: sunk channels glowing orange to yellow.
    s = stroke_distance(xy)
    core = math.exp(-(s / STROKE_HALF_WIDTH) ** 4) * seen  # a broad channel with a hot floor
    halo = math.exp(-(s / (2.2 * STROKE_HALF_WIDTH)) ** 2) * seen
    heat = max(heat + 0.1 * halo, 0.64 + 0.3 * core if core > 0.05 else -9.0)
    lift -= 0.38 * core
    # The white-hot spot swelling out.
    centre, radius = HOT_SPOT
    r = (xy - centre).length
    spot = math.exp(-(r / radius) ** 2) * seen
    heat = max(heat, heat + (0.6 + 0.6 * spot - heat) * smoothstep(0.03, 0.35, spot))
    lift += 0.25 * spot
    # The rim: darker where the ball turns away from the camera (the sprite's dark outline).
    heat -= 0.62 * smoothstep(0.62, 0.0, d.z)
    # Underneath, which the camera never sees, one dark shade (no bands to cut there).
    under = smoothstep(-0.05, -0.4, d.z)
    return heat * (1 - under) + 0.02 * under, lift


def ball_mesh():
    """A unit sphere of even triangles: about 0.45 pixels apart on the ball's top, which the camera sees,
    0.9 round its sides, coarser underneath."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    seen = [e for e in bm.edges if all(v.co.z > -0.3 for v in e.verts)]
    bmesh.ops.subdivide_edges(bm, edges=seen, cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    seen = [e for e in bm.edges if all(v.co.z > 0.45 for v in e.verts)]
    bmesh.ops.subdivide_edges(bm, edges=seen, cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for v in bm.verts:
        v.co.normalize()
    mesh = bpy.data.meshes.new("molten_rock")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("molten_rock", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def materials(shift):
    """The bands' materials, each shift shades hotter (frame 135: 2), glowing in their own colour as strongly
    as the band of that shade (a little more in the hot frame)."""
    mats = []
    for i, (_, index, _) in enumerate(BANDS):
        palette = min(0x7f, index + shift)
        glow = BANDS[min(len(BANDS) - 1, i + shift)][2] * (1.15 if shift else 1.0)
        mats.append(k.material(f"molten_{palette:x}", palette=palette, metallic=0.1, roughness=0.32,
                               emission=k.level_palette()[palette] if glow > 0 else None, emission_strength=glow))
    return mats


def surface_point(d):
    """The ball's point in the direction d: an ellipsoid a little fuller on the diagonals of its plan (the
    sprite's ball is an octagon)."""
    plan = math.atan2(d.y, d.x)
    full = 1.0 + 0.035 * math.sin(2 * plan) ** 2 * (1 - d.z * d.z)
    return CENTRE + Vector((d.x * RADII.x * full, d.y * RADII.y * full, d.z * RADII.z))


def build_ball(shift):
    crust = Crust()
    ball = ball_mesh()
    values = []
    for v in ball.data.vertices:
        d = v.co.normalized()
        point = surface_point(d)
        heat, lift = heat_and_lift(crust, point, d)
        values.append(heat)
        v.co = point + d * lift
    band_split(ball, values, [(lowest, mat) for (lowest, _, _), mat in zip(BANDS, materials(shift))])
    k.smooth(ball, 60)
    # Standing on z = 0 (the game centres it in height on its layer anyway).
    low = min(v.co.z for v in ball.data.vertices)
    ball.data.transform(Matrix.Translation((0.0, 0.0, -low)))
    return ball


def main():
    options = k.args()
    out = mk.outdir(options)
    for name, sprite, shift in FRAMES:
        k.reset()
        ball = build_ball(shift)
        if "check" in options:
            mk.compare("%s (3 %d)" % (name, sprite), mk.coverage([ball], 12, 14),
                       k.sprite_mask(os.path.join(options["check"], "enemy_3.png"), sprite, large=False))
        mk.report(name, [ball], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [ball], size=(12, 14), scale=32)


if __name__ == "__main__":
    main()
