"""Enemies of wave 2, batch H, modelled as their sprites look (models.cfg: yaw=0 unless noted). (GYGES' bronze
ingot, H 93: polish_yuanbao.py; the molten rock ball, L 115 and 3 134: polish_molten_rock.py; the rock arch's
nub, 3 180: polish_rock_arch.py; the fire flaps, A 237 and others: polish_fire_gate.py.)

- asteroid_lumpy (sheet D 5): a grey faceted asteroid.
(brain_clamp, sheet 5 166, and eyespy_eye, 5 202, are built by polish_<name>.py; the claw ship, 3 8 and 3 10, by
polish_twin_claw.py.)

usage: Blender -b --factory-startup -P wave2_h.py -- [--only name,name] [--preview <prefix>]
       [--check <TYR3D_EXTRACT sheets dir>] [--stats 1]
--preview renders <prefix><name>_top.png and _3q.png, --check prints each model's silhouette overlap
with its sprite, --stats the triangles per part. Helpers: wave2_h_kit.py.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave2_h_kit as kit  # noqa: E402
from wave2_h_kit import G2, k, pal  # noqa: E402

# --- D 5: the asteroid ---------------------------------------------------------------------------

ASTEROID = G2.art("""
........................
......00000000000.......
.....0022222222100......
....0024743476322000....
....012523435632221000..
...002333477552334222000
..0022235445753355654210
..0134334755474347742420
..0244323787674457964322
..0245564469854579432332
..0244774333544774422222
..0024432244433453523220
...002322367343344432320
....02222322544244323210
....01222233433244322200
....0012224323222222210.
.....002234542222222100.
......0122543322100000..
......001232222100......
.......0011111100.......
........00000000........
""")


def _ray_polygon(poly, origin, direction):
    """The nearest distance along a ray from inside a polygon to its outline."""
    best = 1e9
    ox, oy = origin
    dx, dy = direction
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
        ex, ey = bx - ax, by - ay
        den = dx * ey - dy * ex
        if abs(den) < 1e-12:
            continue
        t = ((ax - ox) * ey - (ay - oy) * ex) / den
        u = ((ax - ox) * dy - (ay - oy) * dx) / den
        if t > 1e-6 and -1e-9 <= u <= 1 + 1e-9:
            best = min(best, t)
    return best


def asteroid_lumpy():
    """A grey asteroid over the sprite's lumpy outline: a lumpy blob through the outline, its
    surface broken into flat facets of different sizes and shades."""
    shades = [pal(f"rock_{i:x}", i, metallic=0.1, roughness=0.75)
              for i in (0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c)]
    poly = max(G2.polys(ASTEROID, "0123456789", smooth=2, epsilon=0.3), key=len)
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    height = 6.8
    centre = Vector((cx, cy, height))
    rng = random.Random(5)
    waves = [(Vector([rng.uniform(-1, 1) for _ in range(3)]).normalized() * rng.uniform(2.5, 5.5),
              rng.uniform(0, 6.3)) for _ in range(10)]

    def blob(n):
        theta = math.atan2(n.y, n.x)
        r = _ray_polygon(poly, (cx, cy), (math.cos(theta), math.sin(theta))) - 0.1
        lumps = 1 + 0.12 * sum(math.sin(w.dot(n) + phase) for w, phase in waves) / len(waves) ** 0.5
        lumps = 1 + (lumps - 1) * min(1.0, abs(n.z) * 2.0)  # the outline stays the sprite's
        return centre + Vector((n.x * r * lumps, n.y * r * lumps, n.z * height * lumps))

    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    for v in bm.verts:
        n = v.co.normalized()
        jitter = 1 + rng.uniform(-0.04, 0.04) * min(1.0, abs(n.z) * 2.0)
        v.co = centre + (blob(n) - centre) * jitter
    # Faces that lie nearly in one plane become one facet.
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(11), verts=bm.verts[:], edges=bm.edges[:])
    patches = [(Vector([rng.uniform(-1, 1) for _ in range(3)]).normalized() * rng.uniform(0.35, 0.7),
                rng.uniform(0, 6.3)) for _ in range(6)]
    for f in bm.faces:
        # Lighter and darker patches, each facet a shade or two off its patch.
        c = f.calc_center_median()
        field = sum(math.sin(w.dot(c) + phase) for w, phase in patches) / len(patches) ** 0.5
        shade = 4.2 + 2.6 * field + rng.choice((-1, 0, 0, 1))
        f.material_index = max(0, min(len(shades) - 1, int(round(shade))))
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("asteroid")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("asteroid", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m in shades:
        obj.data.materials.append(m)
    k.smooth(obj, 5)


# --- Building ------------------------------------------------------------------------------------

E = kit.ENEMIES
MODELS = [
    ("asteroid_lumpy", asteroid_lumpy, [("D", 5, True)], E),
]

kit.run(MODELS)
