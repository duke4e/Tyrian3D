"""The ball of molten lava of SURFACE, LAVA EXIT, INVADERS and COLLECTOR (sheet 5 sprite 51, 2x2: a
23 x 23 ball in the 24 x 28 cell), polished (2026-10-18; it replaces later_episodes.py's plain
glowing sphere). models.cfg: sprite 5 51 lava_ball.

As the 4x upscale draws it: a lumpy ball of glowing cells, orange to yellow-white, swelling out
between red veins that run round them; hotter towards the lower right (the sprite's yellow
there), cooler and redder towards the upper left, and a darker crust round its edge (the sprite's
dark purple outline).

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.
"""
import math
import os
import random
import sys

import bmesh
import mathutils.noise as noise
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import bpy  # noqa: E402
import tyrkit as k  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_sphere_nozzle import arc, fibonacci_points, smoothstep  # noqa: E402

CENTRE = Vector((0.5, 0.5, 0.0))  # the sprite's columns 1-23, rows 2-24
RADII = Vector((11.2, 11.2, 10.4))
MEAN_RADIUS = 11.0
CELLS = 34
SEED = 51
HOT_SIDE = Vector((0.45, -0.55, 0.7)).normalized()  # the lower right, towards the camera

# The bands of heat: (lowest heat, palette index, emission strength in the palette colour).
BANDS = [
    (-9.0, 0x71, 0.0),
    (0.06, 0x74, 0.3),
    (0.18, 0x76, 0.7),
    (0.32, 0x78, 1.0),
    (0.45, 0x79, 1.2),
    (0.56, 0x7a, 1.4),
    (0.66, 0x7b, 1.6),
    (0.76, 0x7c, 1.8),
    (0.87, 0x7d, 2.0),
    (0.98, 0x7e, 2.3),
]


class Cells:
    """Cells of the crust: the Voronoi cells of random points on the ball, some grown at their
    neighbours' cost."""

    def __init__(self):
        rng = random.Random(SEED)
        self.seeds = fibonacci_points(CELLS, rng, jitter=0.7)
        self.weights = [rng.uniform(0.0, 0.12) for _ in self.seeds]
        self.heat = [rng.uniform(-0.1, 0.12) for _ in self.seeds]  # some cells hotter than others
        self.swell = [rng.uniform(0.25, 0.55) for _ in self.seeds]

    def nearest(self, p):
        """The nearest cell and the distance to its edge (pixels)."""
        d = sorted((arc(p, s) - w, i) for i, (s, w) in enumerate(zip(self.seeds, self.weights)))[:2]
        return d[0][1], (d[1][0] - d[0][0]) / 2 * MEAN_RADIUS


def heat_and_lift(cells, p):
    """The heat (0: the red veins, 1 and more: white hot) at the direction p, and how far the
    surface is raised there."""
    i, edge = cells.nearest(p)
    inside = smoothstep(0.12, 1.5, edge)
    heat = 0.1 + 0.55 * inside + cells.heat[i] * inside
    heat += 0.22 * p.dot(HOT_SIDE)
    heat += 0.06 * noise.noise(p * 3.0 + Vector((2.0, 7.0, 1.0)))
    # The crust round the edge, as the camera sees it from above.
    heat -= 0.32 * smoothstep(0.32, 0.0, p.z)
    lift = cells.swell[i] * math.sqrt(smoothstep(0.0, 1.6, edge)) - 0.3
    lift += 0.45 * noise.noise(p * 1.4 + Vector((5.0, 3.0, 8.0)))
    return heat, lift


def ball_mesh():
    """A unit sphere of even triangles, twice as fine on the side the game's camera sees."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    seen = [e for e in bm.edges if all(v.co.z > 0.05 for v in e.verts)]
    bmesh.ops.subdivide_edges(bm, edges=seen, cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for v in bm.verts:
        v.co.normalize()
    mesh = bpy.data.meshes.new("lava_ball")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("lava_ball", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def build():
    k.reset()
    mats = {}
    for _, index, glow in BANDS:
        mats[index] = k.material(f"lava_{index:x}", palette=index, roughness=0.45,
                                 emission=k.level_palette()[index] if glow > 0 else None, emission_strength=glow)
    cells = Cells()
    ball = ball_mesh()
    values = []
    for v in ball.data.vertices:
        p = v.co.normalized()
        heat, lift = heat_and_lift(cells, p)
        values.append(heat)
        v.co = CENTRE + Vector((p.x * RADII.x, p.y * RADII.y, p.z * RADII.z)) + p * lift
    band_split(ball, values, [(lowest, mats[index]) for lowest, index, _ in BANDS])
    k.smooth(ball, 70)
    print("triangles:", sum(len(p.vertices) - 2 for p in ball.data.polygons), "materials:", len(ball.data.materials))

    # The game shows colours as they are (no filmic tone mapping): so do the previews.
    bpy.context.scene.view_settings.view_transform = "Standard"
    k.finish(os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies", "lava_ball.glb"))


if __name__ == "__main__":
    build()
