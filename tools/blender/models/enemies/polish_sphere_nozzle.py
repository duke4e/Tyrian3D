"""The pitted sphere with the glowing nozzle (sheet K sprite 81, 2x2: 24 x 28 pixels; CAMANIS;
models.cfg: sprite k 81 sphere_nozzle yaw=0).

A light blue-grey metal ball (the sprite's ramp 6, columns 4-22 of rows 4-20) whose shell is
crumpled into plates: each plate tilted a little its own way, dark cracks between them and a few
round pits with raised rims, as the 4x upscale draws it. From its lower right a short steel nozzle
sticks out towards the lower right of the screen and up towards the camera (columns 15-23 of rows
12-21): a collar where it leaves the shell, a flared barrel with a rounded lip, and in its mouth
a glowing bulb, dark red at its rim, orange, yellow and white-hot in the middle (the sprite's ramp
7). The nozzle points up enough for its mouth to face the camera, as the sprite shows the glowing
disc nearly round.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.

Polish (2026-10-18): replaces later_episodes.py's orbs() sphere_nozzle (a plain ellipsoid and a cone).
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402

# The ball: its centre (pixel 13.5, 12.5) and radii (19 x 17 pixels in the sprite; deeper towards
# the camera so that it reads as a ball from the game's slanted view).
CENTRE = Vector((1.5, 1.5, 4.5))
RADII = Vector((9.35, 8.45, 8.9))
MEAN_RADIUS = 8.9

# The nozzle's axis: towards the mouth (the glowing disc, pixel ~21, 18.5) in plan, raised by
# ELEVATION towards the camera. Distances along it are measured from the ball's centre.
PLAN = Vector((7.5, -6.0)).normalized()
ELEVATION = math.radians(40)
AXIS = Vector((PLAN.x * math.cos(ELEVATION), PLAN.y * math.cos(ELEVATION), math.sin(ELEVATION)))
MOUTH = 13.0            # the lip's front, along the axis

PLATES = 38             # crumpled plates on the shell
CRACK_HALF_WIDTH = 0.45  # the groove along a plate's edge, either side (pixels)
CRACK_DEPTH = 0.42
CRACK_PAINT = 0.5       # the dark line: where the groove is this deep (0-1), up to about 0.6 px wide
PIT_PAINT = 0.42        # a pit's dark floor
SEED = 81
DISSOLVE_ANGLE = 4.0  # degrees


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


# --- The shell ------------------------------------------------------------------------------------

def fibonacci_points(count, rng, jitter=0.35):
    """Points spread evenly over the unit sphere, each moved a little at random."""
    points = []
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(count):
        z = 1 - 2 * (i + 0.5) / count
        r = math.sqrt(1 - z * z)
        a = golden * i
        p = Vector((r * math.cos(a), r * math.sin(a), z))
        p += Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * jitter * math.sqrt(4 / count)
        points.append(p.normalized())
    return points


def tangent_vector(p, rng, size):
    """A random vector of the given length tangent to the unit sphere at p."""
    v = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)))
    v -= p * v.dot(p)
    return v.normalized() * size if v.length > 1e-6 else Vector((0, 0, 0))


def arc(p, q):
    return math.acos(max(-1.0, min(1.0, p.dot(q))))


class Shell:
    """The crumpled shell's relief: plates (Voronoi cells of random seeds on the sphere), each
    raised and tilted its own way, a groove along their edges, round pits with raised rims and a
    few broad dents and bulges that keep the ball from looking turned."""

    def __init__(self):
        rng = random.Random(SEED)
        self.seeds = fibonacci_points(PLATES, rng, jitter=0.6)
        # Weights (radians) that grow some plates at their neighbours' cost and bend their edges.
        self.weights = [rng.uniform(0.0, 0.09) for _ in self.seeds]
        self.offsets = [rng.uniform(-0.22, 0.24) for _ in self.seeds]
        self.tilts = [tangent_vector(s, rng, rng.uniform(0.09, 0.25)) for s in self.seeds]
        # How deep the crack between two plates is (and so how wide its dark line).
        self.edge_depth = {}
        for i in range(len(self.seeds)):
            for j in range(i + 1, len(self.seeds)):
                self.edge_depth[(i, j)] = rng.uniform(0.6, 1.0)
        # Pits (centre direction, radius in pixels), most of them on the side the camera sees.
        self.pits = [(Vector(d).normalized(), r) for d, r in (
            ((-0.45, 0.35, 0.82), 1.3), ((0.25, 0.55, 0.8), 0.95), ((-0.2, -0.3, 0.93), 1.1),
            ((-0.8, -0.1, 0.55), 1.0), ((0.05, -0.75, 0.66), 0.9))]
        # Broad dents and bulges (direction, radius in pixels, height).
        self.lumps = [(Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.3, 1))).normalized(),
                       rng.uniform(3.5, 6.0), rng.choice((-1, 1)) * rng.uniform(0.25, 0.5)) for _ in range(7)]

    def plate_term(self, i, p):
        return self.offsets[i] + self.tilts[i].dot(p - self.seeds[i]) * MEAN_RADIUS

    def edge(self, p):
        """The two nearest plates and the distance to their common edge (pixels)."""
        d = sorted((arc(p, s) - w, i) for i, (s, w) in enumerate(zip(self.seeds, self.weights)))[:2]
        return d[0][1], d[1][1], (d[1][0] - d[0][0]) / 2 * MEAN_RADIUS

    def crack(self, p):
        """The groove's depth at p, 0-1 (1 on the edge of two plates with a full crack)."""
        i1, i2, edge = self.edge(p)
        return self.edge_depth[(min(i1, i2), max(i1, i2))] * (1 - smoothstep(0.0, CRACK_HALF_WIDTH * 1.5, edge))

    def pit(self, p):
        """The deepest pit's depth at p, 0-1."""
        return max(max(0.0, 1 - (arc(p, c) * MEAN_RADIUS / r) ** 2) for c, r in self.pits)

    def displacement(self, p):
        i1, i2, edge = self.edge(p)
        # The plates, blended into each other at their edge so that the groove's floor is smooth.
        w = smoothstep(0.0, 0.7, edge)
        d = self.plate_term(i1, p) * (0.5 + 0.5 * w) + self.plate_term(i2, p) * (0.5 - 0.5 * w)
        d -= CRACK_DEPTH * self.crack(p)
        for centre, radius in self.pits:
            t = arc(p, centre) * MEAN_RADIUS
            if t < radius * 2.0:
                d += -0.62 * max(0.0, 1 - (t / radius) ** 2) ** 1.5 + 0.2 * math.exp(-((t - radius) / (0.45 * radius)) ** 2)
        for centre, radius, height in self.lumps:
            t = arc(p, centre) * MEAN_RADIUS
            d += height * math.exp(-(t / radius) ** 2)
        return d


def split_along(bm, values, threshold):
    """Cuts the faces along the contour where the vertex values (a dict) cross threshold, so
    that the materials on either side meet along a smooth line rather than along the faces'
    edges. The new vertices get the threshold as their value."""
    made = set()
    for e in list(bm.edges):
        a, b = e.verts
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


def shell(plate_mat, crack_mat, pit_mat):
    relief = Shell()
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    # Twice as fine where the game's camera sees the ball (from above, a little from the front).
    seen = [e for e in bm.edges if all(v.co.z > 0.12 or (v.co.y < -0.6 and v.co.z > -0.3) for v in e.verts)]
    bmesh.ops.subdivide_edges(bm, edges=seen, cuts=1, use_grid_fill=True)
    for v in bm.verts:
        v.co.normalize()
    # The material borders first, on the round ball: the cracks' and the pits' contours.
    cracks = {v: relief.crack(v.co.normalized()) * smoothstep(-0.5, -0.2, v.co.normalized().z) for v in bm.verts}
    split_along(bm, cracks, CRACK_PAINT)
    pits = {v: relief.pit(v.co.normalized()) for v in bm.verts}
    split_along(bm, pits, PIT_PAINT)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    kinds = []
    for f in bm.faces:
        pit = sum(pits[v] for v in f.verts) / len(f.verts)
        crack = sum(cracks[v] if v in cracks else relief.crack(v.co.normalized()) for v in f.verts) / len(f.verts)
        kinds.append(2 if pit > PIT_PAINT else 1 if crack > CRACK_PAINT else 0)
    # Then the relief: the ellipsoid's surface along each direction, moved out by the relief.
    for v in bm.verts:
        p = v.co.normalized()
        q = Vector((p.x * RADII.x, p.y * RADII.y, p.z * RADII.z))
        v.co = CENTRE + q + p * relief.displacement(p)
    mesh = bpy.data.meshes.new("shell")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("shell", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for mat in (plate_mat, crack_mat, pit_mat):
        obj.data.materials.append(mat)
    for poly, kind in zip(obj.data.polygons, kinds):
        poly.material_index = kind
    k.recalc_normals(obj)
    # Faces that lie nearly flat with their neighbours (on the plates) merged, the cracks' and
    # pits' borders kept.
    mod = obj.modifiers.new("dissolve", "DECIMATE")
    mod.decimate_type = "DISSOLVE"
    mod.angle_limit = math.radians(DISSOLVE_ANGLE)
    mod.delimit = {"MATERIAL"}
    return k.smooth(obj, 42)


# --- The nozzle -----------------------------------------------------------------------------------

def along_axis(obj):
    """Turns a part built along +Y from the ball's centre onto the nozzle's axis."""
    rotation = Vector((0, 1, 0)).rotation_difference(AXIS).to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(CENTRE) @ rotation)
    return obj


def nozzle(steel, collar_mat, bore_mat, glows):
    m = MOUTH
    # The barrel: from inside the ball out to the lip, flaring a little, back into the mouth.
    barrel = k.lathe("barrel", [(7.0, 0.0), (7.0, 2.85), (8.4, 2.95), (m - 2.5, 3.1), (m - 1.1, 3.32), (m - 0.45, 3.48),
                                (m, 3.38), (m + 0.08, 3.1), (m, 2.78), (m - 0.35, 2.66), (m - 0.65, 2.62),
                                (m - 0.75, 0.0)], steel, segments=20)
    barrel.data.materials.append(bore_mat)
    for poly in barrel.data.polygons:  # the mouth's inner wall
        c = poly.center
        if c.y > m - 0.8 and math.hypot(c.x, c.z) < 2.72 and poly.normal.y < 0.6:
            poly.material_index = 1
    k.smooth(along_axis(barrel), 50)
    # The collar where it leaves the shell.
    collar = k.lathe("collar", [(7.6, 0.0), (7.6, 3.2), (8.0, 3.5), (8.6, 3.62), (9.1, 3.5), (9.35, 3.2),
                                (9.4, 0.0)], collar_mat, segments=20)
    k.smooth(along_axis(collar), 50)
    # The glowing bulb in the mouth: domed out towards the lip, painted in rings from its dark red
    # rim to its white-hot middle.
    profile = [(m - 0.7, 2.64), (m - 0.58, 2.5), (m - 0.4, 2.15), (m - 0.25, 1.7), (m - 0.14, 1.2), (m - 0.07, 0.7),
               (m - 0.04, 0.3), (m - 0.03, 0.0)]
    bulb = k.lathe("bulb", k.profile(profile, step=0.12), glows[0], segments=20)
    for mat in glows[1:]:
        bulb.data.materials.append(mat)
    for poly in bulb.data.polygons:
        r = math.hypot(poly.center.x, poly.center.z)
        poly.material_index = 0 if r > 2.1 else 1 if r > 1.3 else 2 if r > 0.6 else 3
    k.smooth(along_axis(bulb), 60)


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            mesh = obj.evaluated_get(depsgraph).to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            obj.evaluated_get(depsgraph).to_mesh_clear()
    return total


def build():
    k.reset()
    plate = k.material("snozzle_plate", palette=110, metallic=0.35, roughness=0.32)
    crack = k.material("snozzle_crack", palette=105, metallic=0.25, roughness=0.6)
    pit = k.material("snozzle_pit", palette=106, metallic=0.3, roughness=0.5)
    steel = k.material("snozzle_steel", palette=10, metallic=0.45, roughness=0.26)
    collar = k.material("snozzle_collar", palette=8, metallic=0.45, roughness=0.3)
    bore = k.material("snozzle_bore", palette=3, metallic=0.3, roughness=0.5)
    glows = [k.material("snozzle_glow_red", palette=119, roughness=0.4, emission=(230, 30, 0), emission_strength=2.2),
             k.material("snozzle_glow_orange", palette=122, roughness=0.4, emission=(255, 130, 20),
                        emission_strength=2.6),
             k.material("snozzle_glow_yellow", palette=125, roughness=0.4, emission=(255, 220, 70),
                        emission_strength=3.0),
             k.material("snozzle_glow_white", palette=127, roughness=0.4, emission=(255, 250, 225),
                        emission_strength=3.4)]

    shell(plate, crack, pit)
    nozzle(steel, collar, bore, glows)

    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    print("triangles:", triangles())
    mouth = CENTRE + AXIS * MOUTH
    print("mouth at (%.2f, %.2f, %.2f)" % tuple(mouth))
    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "sphere_nozzle.glb"))


if __name__ == "__main__":
    build()
