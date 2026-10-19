"""The grey stone plant of TORM, BOTANY B and BONUS (sheet J sprite 1, 2x2: 21 x 25 pixels in the 24 x 28 cell; enemy
750, on the ground; not animated) and its damaged look (J 3, its dgr: the bud shot off, red-hot cracks), polished
(2026-10-19). models.cfg: sprite j 1 stone_plant yaw=0 and sprite j 3 stone_plant_damaged yaw=0 (both unchanged).
No other enemy shows these sprites; they are no other sprites' pixels mirrored or in other ramps.

(stone_plant's old generator, wave2_g.py's stone_plant(), was removed with the horseshoe's in commit 91addff, so
nothing in the repository built assets/models/enemies/stone_plant.glb any more, and wave3_ap_torm.py's
stone_plant_damaged(), which starts from plants.stone_plant(), fails: this script builds both.)

As the sprite and its 4x upscale draw it, in greys (ramp 0) on the ground: a low clump of thick stone leaves round
its foot (rows 18-27), a big leaf curling down its left side (columns 2-8 of rows 15-25, its lit rim the sprite's
0b-0e), a round cup in its middle (columns 9-15 of rows 13-19: dark, its right inner wall lit, a hollow), a stalk
rising from the clump up and to the left (columns 6-9 of rows 10-14) to a bud of two lobes high on it (rows 3-10): a
round lobe on the left and an upright petal on the right whose tip is the sprite's brightest pixel (column 9 of row
4); and at the right a small pointed bud on a short stalk (columns 17-23 of rows 12-19).

Built as one carved stone: the forms are first made as smooth organic shapes (the leaves thick blades along curved
paths, the stalks tapering tubes, the cup turned, the buds pointed and round), then fused into one surface
(a voxel remesh, smoothed and thinned out: polish_machine_kit), so that the stalks grow out of the clump and the
leaves out of each other as in the upscale. That surface is painted by the part each face lies on (the buds and
the curling leaf paler, the clump darker), its fillets where the parts meet dark (the sprite's black crevices), and
pale rims where it faces the light from the upper left (the sprite's 0b-0e edges). The plant stands on the ground
(z = 0); its stalk leans back up the screen, so that from the game's camera the bud stands over the clump where
the sprite draws it.

stone_plant_damaged (J 3): the same plant, sooty (every shade two darker), its bud shot off and the stalk broken
short in a jagged ring with a dark hollow (the sprite's ring at rows 10-13), red-hot cracks glowing down the stalk's
foot (columns 7 and 9 of rows 15-21) and through the cup (columns 12-14 of rows 19-25), laid on its surface.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.

Replaces wave3_ap_torm.py's stone_plant_damaged() (its @w.model("stone_plant_damaged", [(J, 3, True)]) function, the
plants = kit.load("wave2_g") line, which only it reads, and the stone_plant_damaged lines of the docstring),
wave3_ap_art.py's J1_DMG and wave2_g_art.py's J1 (only it reads them), and the stone_plant line of wave2_g.py's
docstring: remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each model's silhouette
against its sprite in enemy_J.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402
from polish_jets import triangles  # noqa: E402
from polish_squid_ship import catmull, tube  # noqa: E402

# The fused surface: the remesh's voxel size, the smoothing, the triangles kept; the fillets painted dark where a
# face lies further than CREVICE outside every part; the rims pale where the normal faces LIGHT more than RIM.
VOXEL, SMOOTH_ITERATIONS, TRIANGLES = 0.18, 2, 8000
CREVICE = 0.09
LIGHT = Vector((-0.5, 0.45, 0.74)).normalized()
RIM, PALE = 0.8, 0.9
# The tone of each part: (its material, whether it takes pale rims).
TONES = {"mound": ("foot", False), "foot_leaf": ("leaf", True), "curl_leaf": ("curl", True), "bulb": ("bulb", True),
         "stalk": ("stalk", True), "bud": ("bud", True), "side_stalk": ("stalk", True), "side_bud": ("bud", True),
         "crevice": ("dark", False)}


def P(c, r, z=0.0):
    """A pixel's centre (column c, row r) of the 24 x 28 cell, at height z."""
    return Vector((c + 0.5 - 12.0, 13.5 - r, z))


def materials(soot=0):
    """The stone's materials; soot darkens every shade by that many steps (the damaged plant)."""
    def stone(key, index, rough=0.5):
        return k.material(f"plant_{key}", palette=max(1, index - soot), metallic=0.1, roughness=rough)
    pal = k.level_palette()
    return {
        "foot": stone("foot", 0x04, 0.6),
        "leaf": stone("leaf", 0x05, 0.5),
        "curl": stone("curl", 0x07, 0.45),
        "bulb": stone("bulb", 0x06, 0.42),
        "stalk": stone("stalk", 0x05, 0.5),
        "bud": stone("bud", 0x08, 0.38),
        "rim": stone("rim", 0x0a, 0.4),
        "pale": stone("pale", 0x0c, 0.35),
        "dark": stone("dark", 0x02, 0.8),
        "crack": k.material("plant_crack", palette=0x76, metallic=0.0, roughness=0.4, emission=pal[0x76],
                            emission_strength=1.5),
        # The parts' own materials before they are fused (not exported).
        "stone": stone("stone", 0x05, 0.5),
        "stone_light": stone("stone_light", 0x08, 0.5),
    }


def roughen(obj, amount=0.18, scale=0.55, seed=0.0):
    """Moves each vertex along its normal by smooth noise (a stone's uneven surface)."""
    mesh = obj.data
    mesh.update()
    for v in mesh.vertices:
        n = noise.noise(v.co * scale + Vector((seed, 2 * seed, 0.5 * seed)))
        v.co += v.normal * amount * n
    return obj


def blob(name, centre, radii, mat, segments=24, rings=12, amount=0.15, seed=0.0, flat=None):
    obj = k.ellipsoid(name, tuple(centre), tuple(radii), mat, segments, rings)
    roughen(obj, amount, seed=seed)
    if flat is not None:  # flattened underneath at z = flat
        for v in obj.data.vertices:
            v.co.z = max(v.co.z, flat)
    return k.smooth(obj, 60)


def blade(name, path, widths, heights, mat, rim_mat=None, segments=14, lean=None, seed=0.0):
    """A thick leaf along a path of points (Vectors): its half-width across (in plan) and its half-height along it;
    its outer edge (the left of the path's direction, or the side `lean` gives per point) a paler rim."""
    rings = []
    n = len(path)
    for i, p in enumerate(path):
        a, b = path[max(i - 1, 0)], path[min(i + 1, n - 1)]
        t = (b - a)
        t.z = 0.0
        t.normalize()
        side = Vector((-t.y, t.x, 0.0))  # to the left of the direction
        ring = []
        for j in range(segments):
            ang = 2 * math.pi * j / segments
            c, s = math.cos(ang), math.sin(ang)
            q = p + side * (c * widths[i]) + Vector((0, 0, 1)) * (s * heights[i] * (1.0 if s > 0 else 0.6))
            ring.append(q)
        rings.append(ring)
    t0 = (path[1] - path[0]).normalized()
    t1 = (path[-1] - path[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=path[0] - t0 * widths[0] * 0.6,
                 end_point=path[-1] + t1 * max(widths[-1], 0.1) * 0.6)
    roughen(obj, 0.1, seed=seed)
    if rim_mat is not None:
        obj.data.materials.append(rim_mat)
        for poly in obj.data.polygons:
            ring_i, j = divmod(poly.index, segments)
            if ring_i >= n - 1:
                continue
            ang = 2 * math.pi * (j + 0.5) / segments
            if math.cos(ang) > 0.55 and math.sin(ang) > -0.2:  # the outer upper edge
                poly.material_index = 1
    return k.smooth(obj, 55)


def taper(path, r0, r1):
    n = len(path)
    return [r0 + (r1 - r0) * i / max(n - 1, 1) for i in range(n)]


def teardrop(name, base, tip, radius, mat, squash=0.85, belly=0.36, segments=28, rings=20, seed=0.0,
             crease_mat=None):
    """A bud: turned about the line from base to tip, round at its base (fattest `belly` of the way up) and drawn
    to a point at its tip, a little flattened across (squash); if crease_mat, a dark crease down its upper side from
    the tip (the line where its two petals close)."""
    axis = tip - base
    t_dir = axis.normalized()
    side = t_dir.cross(Vector((0, 0, 1)))
    if side.length < 1e-6:
        side = Vector((1, 0, 0))
    side.normalize()
    up = side.cross(t_dir).normalized()

    def radius_at(t):
        if t < belly:
            return radius * math.sin(0.5 * math.pi * t / belly) ** 0.8
        return radius * math.cos(0.5 * math.pi * (t - belly) / (1 - belly)) ** 1.2
    out = []
    for i in range(1, rings):
        t = i / rings
        r = radius_at(t)
        c = base + axis * t
        out.append([c + side * (math.cos(2 * math.pi * j / segments) * r) +
                    up * (math.sin(2 * math.pi * j / segments) * r * squash) for j in range(segments)])
    obj = k.loft(name, out, mat, start_point=base, end_point=tip)
    roughen(obj, 0.08, seed=seed)
    k.smooth(obj, 60)
    if crease_mat is not None:
        line = []
        for i in range(12):
            t = 0.3 + 0.68 * i / 11
            line.append(base + axis * t + up * (radius_at(t) * squash - 0.12))
        tube(name + "_crease", line, [0.26 * min(1.0, 0.4 + i / 4) * (1 - 0.6 * i / 11) for i in range(12)],
             crease_mat, segments=6, squash=0.6)
    return obj


def build_parts(m, damaged=False):
    """The plant's forms before they are fused (each named after its tone in TONES); damaged: its bud shot off, the
    stalk broken short (J 3)."""
    # The clump of leaves round the foot (rows 18-27): a low mound and thick leaves lying out from it.
    blob("mound", P(11.2, 22.4, 0.3), (8.6, 4.9, 2.7), m["stone"], 30, 12, amount=0.22, seed=1.0, flat=0.0)
    leaves = [
        # (path in pixels (column, row, z), half-widths, half-heights)
        ([(11.5, 21.5, 1.9), (13.5, 22.8, 1.9), (15.5, 23.6, 1.6), (17.5, 23.3, 1.2), (19.4, 21.8, 0.9)],
         [1.8, 2.1, 1.9, 1.4, 0.6], [1.4, 1.5, 1.3, 1.0, 0.55]),
        ([(10.5, 22.5, 1.9), (9.5, 24.3, 1.6), (8.0, 25.7, 1.2), (6.0, 26.2, 0.9)],
         [1.7, 2.0, 1.6, 0.6], [1.4, 1.3, 1.0, 0.55]),
        ([(12.5, 24.0, 1.6), (13.0, 25.7, 1.3), (14.6, 26.7, 1.0), (16.3, 26.3, 0.8)],
         [1.6, 1.7, 1.2, 0.5], [1.2, 1.1, 0.9, 0.45]),
        ([(14.0, 20.5, 2.4), (16.0, 20.6, 2.2), (18.0, 19.7, 1.7), (19.4, 18.6, 1.2)],
         [1.6, 1.8, 1.4, 0.6], [1.3, 1.3, 1.1, 0.55]),
    ]
    for i, (pts, widths, heights) in enumerate(leaves):
        path = catmull([P(*p) for p in pts], 0.5)
        n = len(path)
        w = [widths[min(len(widths) - 1, int(j / (n - 1) * (len(widths) - 1) + 0.5))] for j in range(n)]
        h = [heights[min(len(heights) - 1, int(j / (n - 1) * (len(heights) - 1) + 0.5))] for j in range(n)]
        for _ in range(3):  # smooth the steps of the widths
            w = [w[0]] + [(w[j - 1] + 2 * w[j] + w[j + 1]) / 4 for j in range(1, n - 1)] + [w[-1]]
            h = [h[0]] + [(h[j - 1] + 2 * h[j] + h[j + 1]) / 4 for j in range(1, n - 1)] + [h[-1]]
        blade(f"foot_leaf{i}", path, w, h, m["stone"], seed=3.0 + i)
    # The big leaf curling down the left side, from behind the bulb round to the foot.
    pts = [(8.6, 15.4, 3.4), (6.5, 15.5, 3.8), (4.6, 16.8, 3.8), (3.4, 19.0, 3.5), (3.2, 21.5, 3.0), (4.0, 23.6, 2.4),
           (5.8, 24.9, 1.8), (8.0, 24.7, 1.5)]
    path = catmull([P(*p) for p in pts], 0.45)
    n = len(path)
    w = [1.2 + 1.3 * math.sin(math.pi * min(1.0, j / (n - 1) * 1.1)) for j in range(n)]
    h = [1.25 + 0.85 * math.sin(math.pi * j / (n - 1)) for j in range(n)]
    blade("curl_leaf", path, w, h, m["stone"], seed=7.0)
    # The cup in the middle (the sprite's dark round with its right wall lit: a hollow).
    cup = mk.lathe("bulb", [(0.01, 0.4), (2.6, 0.7), (3.6, 1.6), (3.95, 2.9), (3.75, 3.9), (3.3, 4.35), (2.75, 4.2),
                            (2.3, 3.6), (1.5, 3.05), (0.01, 2.9)], tuple(P(12.3, 16.5)[:2]), m["stone"], segments=32,
                   squash=(1.0, 0.88))
    roughen(cup, 0.1, seed=11.0)
    k.smooth(cup, 50)
    # The small bud at the right, on its short stalk.
    pts = [P(17.2, 19.4, 1.4), P(18.6, 17.9, 2.4), P(19.6, 16.8, 3.1)]
    path = catmull(pts, 0.4)
    tube("side_stalk", path, taper(path, 1.2, 0.9), m["stone"], segments=12)
    teardrop("side_bud", P(19.9, 17.6, 2.6), P(20.4, 11.6, 5.6), 2.35, m["stone"], squash=0.8, seed=23.0)
    # The stalk rising from the clump up and to the left, leaning back, to the bud.
    pts = [P(8.9, 17.4, 1.8), P(8.2, 14.6, 4.0), P(7.5, 12.6, 5.6), P(7.0, 11.0, 6.6), P(6.6, 9.4, 7.5)]
    if damaged:
        pts = pts[:4]
    path = catmull(pts, 0.4)
    stalk = tube("stalk", path, taper(path, 2.1, 1.5 if not damaged else 1.7), m["stone"], segments=14, squash=0.9)
    roughen(stalk, 0.08, seed=13.0)
    if damaged:
        # The broken end: a jagged ring of stone round the stalk's top (the sprite's ring at rows 10-13).
        end, direction = path[-1], (path[-1] - path[-2]).normalized()
        side = direction.cross(Vector((0, 0, 1))).normalized()
        up = side.cross(direction).normalized()
        ring = []
        for j in range(25):
            a = 2 * math.pi * j / 24
            jag = 0.35 * math.sin(5 * a + 1.0) + 0.2 * math.sin(9 * a)
            ring.append(end + direction * (0.25 + jag) + (side * math.cos(a) + up * math.sin(a)) * 1.45)
        tube("stalk_stump", ring, [0.5] * len(ring), m["stone"], segments=8)
        return
    # The bud: a round lobe on the left and a pointed petal on the right closing on it, its tip (the sprite's
    # brightest pixel) up and to the right; the crease between them is the fused surface's fillet.
    blob("bud_lobe", P(6.0, 7.7, 8.0), (2.85, 2.6, 2.35), m["stone"], 26, 13, amount=0.1, seed=17.0)
    teardrop("bud_petal", P(8.1, 10.3, 7.0), P(9.6, 3.5, 10.6), 2.35, m["stone"], squash=0.8, belly=0.3, seed=19.0)


def tone_of(name):
    for key in sorted(TONES, key=len, reverse=True):
        if name.startswith(key):
            return TONES[key]
    return ("leaf", True)


def fuse(m):
    """The parts fused into one surface, painted by the part each face lies on, dark in the fillets, pale where it
    faces the light. Returns the new object (the parts are removed)."""
    parts = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [(tone_of(o.name), BVHTree.FromObject(o, depsgraph)) for o in parts]
    bm = bmesh.new()
    for o in parts:
        bm.from_mesh(o.data)
    mesh = bpy.data.meshes.new("stone_plant")
    bm.to_mesh(mesh)
    bm.free()
    for o in parts:
        bpy.data.objects.remove(o)
    obj = bpy.data.objects.new("stone_plant", mesh)
    bpy.context.scene.collection.objects.link(obj)
    remesh = obj.modifiers.new("remesh", "REMESH")
    remesh.mode = "VOXEL"
    remesh.voxel_size = VOXEL
    smooth = obj.modifiers.new("smooth", "SMOOTH")
    smooth.factor = 0.5
    smooth.iterations = SMOOTH_ITERATIONS
    mk.apply(obj)
    obj.data.calc_loop_triangles()
    count = len(obj.data.loop_triangles)
    if count > TRIANGLES:
        decimate = obj.modifiers.new("decimate", "DECIMATE")
        decimate.ratio = TRIANGLES / count
        mk.apply(obj)
    for v in obj.data.vertices:  # it stands on the ground
        v.co.z = max(v.co.z, 0.0)
    obj.data.update()
    keys = ["foot", "leaf", "curl", "bulb", "stalk", "bud", "rim", "pale", "dark"]
    hollow = getattr(fuse, "hollow", None)  # the broken stalk's open end (the damaged plant)
    for key in keys:
        obj.data.materials.append(m[key])
    for poly in obj.data.polygons:
        c = poly.center
        best = None
        for (tone, rims), tree in trees:
            loc, normal, _, dist = tree.find_nearest(c)
            if loc is None:
                continue
            outside = (c - loc).dot(normal) > 0
            if best is None or dist < best[0]:
                best = (dist, outside, tone, rims)
        dist, outside, tone, rims = best
        key = tone
        if outside and dist > CREVICE:
            key = "dark"
        elif hollow is not None and (c - hollow).length < 1.05 and poly.normal.z > 0.2:
            key = "dark"
        elif rims:
            lit = poly.normal.dot(LIGHT)
            key = "pale" if lit > PALE else "rim" if lit > RIM else tone
        poly.material_index = keys.index(key)
    # Drop the materials no face took.
    used = {p.material_index for p in obj.data.polygons}
    for i in reversed(range(len(obj.data.materials))):
        if i not in used:
            obj.data.materials.pop(index=i)
    return k.smooth(obj, 60)


# The damaged plant's glowing cracks (J 3): paths in the top view (column, row), laid on its surface.
CRACKS = [[(7.2, 14.8), (7.0, 16.2), (7.1, 17.6), (7.4, 18.8)],
          [(9.2, 14.6), (9.4, 16.4), (9.5, 18.4), (9.6, 20.4), (9.9, 21.6)],
          [(14.3, 18.8), (13.8, 20.2), (13.0, 21.6), (12.5, 23.2), (12.3, 24.8)]]


def cracks(obj, m):
    tree = BVHTree.FromObject(obj, bpy.context.evaluated_depsgraph_get())
    for i, path in enumerate(CRACKS):
        pts = []
        for c, r in [q for q in mk.chaikin(path, 2, closed=False)]:
            x, y, _ = P(c, r)
            hit, _, _, _ = tree.ray_cast(Vector((x, y, 50.0)), Vector((0, 0, -1)))
            if hit is not None:
                pts.append(hit - Vector((0, 0, 0.08)))
        if len(pts) >= 2:
            n = len(pts)
            tube(f"crack{i}", pts, [0.42 * min(1.0, 0.45 + j / 2, 0.45 + (n - 1 - j) / 2) for j in range(n)],
                 m["crack"], segments=8, squash=0.55)


MODELS = [("stone_plant", 1, False), ("stone_plant_damaged", 3, True)]


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, damaged in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        m = materials(soot=2 if damaged else 0)
        build_parts(m, damaged)
        fuse.hollow = None
        if damaged:
            stump = bpy.data.objects["stalk_stump"]
            fuse.hollow = sum((v.co for v in stump.data.vertices), Vector()) / len(stump.data.vertices)
        plant = fuse(m)
        if damaged:
            cracks(plant, m)
        used = {mat.name for o in bpy.context.scene.objects if o.type == "MESH" for mat in o.data.materials}
        print("== %s (J %d): %d triangles, %d materials: %s" % (name, sprite, triangles(), len(used),
                                                             ", ".join(sorted(used))))
        if "check" in options:
            k.check_silhouette(os.path.join(options["check"], "enemy_J.png"), sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
