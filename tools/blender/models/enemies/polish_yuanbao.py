"""GYGES' bronze ingot, the yuanbao (sheet H sprite 93, 2x2: a 20 x 16 ingot in the 24 x 28 cell; enemy 424, 70
in GYGES, sky and top layers; static), polished (2026-10-19; it replaces wave2_h.py's bronze_yuanbao(), a flat
brown fold). models.cfg: sprite h 93 bronze_yuanbao yaw=0.

GYGES strings five of them 10 pixels apart below the bronze worm's head (gyges_worm_head_tip / _base, H 17 above
55) and above its tail (gyges_worm_tail, H 131): each a link of its own that follows the one before, so the worm
is a chain of ingots nested in one another, horns up the screen. Like the head and the tail, which were built
round its height, the ingot is drawn centred in height (no origin).

As the 4x upscale draws it: a glossy dark bronze ingot (the sprite's ramp 1, mostly 0x12-0x19, highlights to
0x1f) seen from the front and a little above: a boat-shaped body whose two ends sweep up into pointed horns
(columns 2-3 and 21-22 of row 5), a round dome rising from the dish between them (columns 7-17 of rows 5-10,
its highlight at the upper left), the dish's dark inside showing between the dome and either horn. The body's
front is a tall face from the light rim (row 11-12 in the middle, rising along the horns' inner edges) down to
the rounded bottom (row 19), creased down its middle: the left facet catches the light, the right one is dark,
a bright glint along the crease (column 12).

The ingot is built standing (+Z its up, -Y its front), then turned about X so that it faces the camera and leans
back TILT degrees, as the sprite shows it from a little above: the dome's top and the dish between the horns
show, the front faces the camera. The body is one loft along its length of rounded sections between its
bottom (rising at either end into the horn's outer edge) and its top, which dips into the dish between a front
and a back rim and rises into the horns; its front is creased down the middle (the crease's edges marked
sharp). The dome is a separate rounded cap standing in the dish. Glossy bronze in the sprite's shades: the rims
lighter, the dish dark.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera. The sprite is symmetric
about column 12's middle (x 0.5): the ingot is built about x = 0 and moved there.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette
against enemy_H.png), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_jets import Curve  # noqa: E402

AXIS_X = 0.5
TILT = 15.0             # degrees the ingot leans back (its top towards the camera)
BOTTOM_Y = -6.45        # the sprite's bottom edge (row 20.45): where the turned ingot's lowest point goes

# The body along its length (a = |x|, standing: z up, -y towards the front), from the middle to the horn tip
# HORN_TIP: the top (the rims), the bottom (flat under the middle, rising at the ends into the horns' outer
# edges), the half-depth (y) at the top and at the bottom, the dish's depth below the rims.
HORN_TIP = 10.6
TOP = Curve([(0.0, 9.3), (2.5, 9.45), (4.5, 9.95), (5.5, 10.6), (6.4, 11.75), (7.2, 12.9), (8.0, 14.0), (8.8, 14.95),
             (9.6, 15.6), (10.3, 15.95), (10.6, 16.05)])
BOTTOM = Curve([(0.0, 0.0), (4.6, 0.0), (5.6, 0.45), (6.7, 1.3), (7.8, 2.6), (8.8, 4.4), (9.5, 6.6), (10.05, 9.0),
                (10.35, 11.4), (10.52, 13.6), (10.6, 15.85)])
HALF_DEPTH_TOP = Curve([(0.0, 4.85), (4.0, 4.8), (6.0, 4.4), (7.5, 3.8), (8.7, 3.15), (9.7, 2.4), (10.3, 1.6),
                        (10.6, 0.45)])
HALF_DEPTH_BOTTOM = Curve([(0.0, 3.45), (4.0, 3.35), (5.5, 3.0), (7.0, 2.55), (8.5, 2.05), (9.7, 1.65), (10.3, 1.25),
                           (10.6, 0.4)])
DISH = Curve([(0.0, 3.4), (4.0, 3.2), (6.0, 2.5), (7.5, 1.3), (8.6, 0.55), (9.6, 0.12), (10.6, 0.0)])
SECTION_POWER = 3.2     # the sections' superellipse (squarer than an ellipse: flat walls, rounded edges)
FLARE = 0.75            # how the walls lean out towards the top (the half-depth's ease from bottom to top)
RIM_WIDTH = 0.36        # the rims: where the dish's slope starts, as a fraction of the half-depth from the edge
# The front's crease down the middle: the front bulges out by CREASE at x = 0, falling off linearly to nothing
# at CREASE_REACH either side (two facets meeting along the crease).
CREASE, CREASE_REACH = 1.7, 6.8
STATIONS = 23           # sections per half (the middle and the tips included), denser towards the tips
SECTION_POINTS = 44

# The dome in the dish: its middle (x, y; standing, +y the back), its foot's height, its height above the foot,
# half-sizes (x, y), and the power of its profile (higher: fuller shoulders).
DOME_CENTRE = (0.0, 0.35)
DOME_FOOT, DOME_HEIGHT = 6.6, 8.5
DOME_RADII = (6.5, 4.4)
DOME_POWER = 2.25

# The colours' borders: the rim's light band (the top within RIM_PAINT of the rim's crest, facing up), the
# dish's dark inside (below DISH_PAINT of the dish's depth under the rims), the body's underside.
RIM_PAINT, DISH_PAINT = 0.55, 0.42
# The sections' points (from the top's middle over the front) that make the front wall and the underside.
FRONT_WALL, UNDER = (5, 17), (17, 28)


def stations():
    """Positions along the length, from -HORN_TIP to HORN_TIP, the middle (the crease) included, denser
    towards the horns."""
    half = [HORN_TIP * math.sin(0.5 * math.pi * i / STATIONS) for i in range(STATIONS)]
    half.append(HORN_TIP - 0.04)
    return [-a for a in reversed(half[1:])] + half


def section(x):
    """The body's cross-section at x (standing: z up, -y the front): points round it, from the top's middle
    over the front, the bottom and the back."""
    a = abs(x)
    top, bottom = TOP(a), BOTTOM(min(a, HORN_TIP))
    d_top, d_bottom = HALF_DEPTH_TOP(a), HALF_DEPTH_BOTTOM(a)
    dish = DISH(a)
    bulge = CREASE * max(0.0, 1.0 - a / CREASE_REACH)
    points = []
    p = SECTION_POWER
    for j in range(SECTION_POINTS):
        t = 2 * math.pi * j / SECTION_POINTS + math.pi / 2   # from the top's middle, towards the front first
        c, s = math.cos(t), math.sin(t)
        cy = -math.copysign(abs(c) ** (2 / p), c)            # +1 at the front
        cz = math.copysign(abs(s) ** (2 / p), s)
        up = (cz + 1) / 2                                     # 0 at the bottom, 1 at the top
        depth = d_bottom + (d_top - d_bottom) * up ** FLARE
        if cy > 0:
            depth += bulge * (0.35 + 0.65 * up)
        y = cy * depth
        z = bottom + (top - bottom) * up
        if cz > 0:  # the dish: the top sinks between the rims
            across = min(1.0, abs(cy) / (1.0 - RIM_WIDTH))
            z -= dish * (1.0 - across ** 2.2) * cz ** 6
        points.append(Vector((x, -y, z)))
    return points


def body(mats):
    xs = stations()
    rings = [section(x) for x in xs]
    tip = lambda sx: (sx * (HORN_TIP + 0.12), 0.0, TOP(HORN_TIP) + 0.05)
    obj = k.loft("body", rings, None, start_point=tip(-1), end_point=tip(1))
    # Colours: the rims' light band, the dish's dark inside, the underside, the front's right facet (away from
    # the sun, darker as the sprite shades it; along the sections' lines), the bronze elsewhere.
    for key in ("bronze", "rim", "dish", "under", "shade"):
        obj.data.materials.append(mats[key])
    n_points = SECTION_POINTS
    middle = len(xs) // 2
    for poly in obj.data.polygons:
        c, n = poly.center, poly.normal
        a = abs(c.x)
        top = TOP(min(a, HORN_TIP))
        i, j = divmod(poly.index, n_points)
        side = poly.index < (len(rings) - 1) * n_points
        if n.z > 0.25 and DISH(a) > 0.4 and c.z < top - DISH_PAINT * DISH(a):
            poly.material_index = 2
        elif n.z > 0.35 and c.z > top - RIM_PAINT and a < HORN_TIP - 0.9:
            poly.material_index = 1
        elif side and FRONT_WALL[1] < j < UNDER[1] and n.z < -0.2:
            poly.material_index = 3
        elif side and i >= middle and FRONT_WALL[0] <= j <= FRONT_WALL[1]:
            poly.material_index = 4
        else:
            poly.material_index = 0
    # The crease: the front's edges along x = 0 sharp, so the two facets meet in a line.
    mesh = obj.data
    for e in mesh.edges:
        v0, v1 = mesh.vertices[e.vertices[0]].co, mesh.vertices[e.vertices[1]].co
        if abs(v0.x) < 1e-4 and abs(v1.x) < 1e-4 and max(v0.y, v1.y) < -0.4 and min(v0.z, v1.z) > 0.6:
            e.use_edge_sharp = True
    return k.smooth(obj, 50)


def dome(mats):
    """A rounded cap standing in the dish: a superellipse profile turned round its axis, its foot sunk."""
    cx, cy = DOME_CENTRE
    rx, ry = DOME_RADII
    rings = []
    count = 14
    for i in range(count):
        t = i / count
        s = (1 - t ** DOME_POWER) ** (1 / DOME_POWER)       # the radius' fraction at height fraction t
        z = DOME_FOOT + DOME_HEIGHT * t
        rings.append([Vector((cx + rx * s * math.cos(2 * math.pi * j / 40),
                              cy + ry * s * math.sin(2 * math.pi * j / 40), z)) for j in range(40)])
    obj = k.loft("dome", rings, mats["dome"], start_point=(cx, cy, DOME_FOOT),
                 end_point=(cx, cy, DOME_FOOT + DOME_HEIGHT))
    return k.smooth(obj, 60)


def materials():
    bronze = dict(metallic=0.5, roughness=0.2)
    return {
        "bronze": k.material("yuanbao_bronze", palette=0x19, **bronze),
        "shade": k.material("yuanbao_shade", palette=0x16, **bronze),
        "rim": k.material("yuanbao_rim", palette=0x1c, metallic=0.5, roughness=0.16),
        "dish": k.material("yuanbao_dish", palette=0x13, metallic=0.45, roughness=0.3),
        "under": k.material("yuanbao_under", palette=0x15, **bronze),
        "dome": k.material("yuanbao_dome", palette=0x1a, metallic=0.5, roughness=0.14),
    }


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            evaluated.to_mesh_clear()
    return total


def place():
    """Stands the ingot up facing the camera, leaning back TILT degrees, its lowest point on the sprite's
    bottom edge, about x = AXIS_X."""
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    # Standing: z up, -y the front. Facing the camera: up becomes +Y, the front +Z; then leaning back.
    turn = Matrix.Rotation(math.radians(TILT), 4, "X") @ Matrix.Rotation(math.radians(-90), 4, "X")
    for obj in meshes:
        obj.data.transform(turn)
    low = min(v.co.y for o in meshes for v in o.data.vertices)
    for obj in meshes:
        obj.data.transform(Matrix.Translation((AXIS_X, BOTTOM_Y - low, 0.0)))


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    mats = materials()
    body(mats)
    dome(mats)
    place()
    used = {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials}
    zs = [v.co.z for o in bpy.context.scene.objects if o.type == "MESH" for v in o.data.vertices]
    print("== bronze_yuanbao (H 93): %d triangles, %d materials, z %.2f to %.2f" % (triangles(), len(used), min(zs),
                                                                                   max(zs)))
    sheet = options.get("check")
    if sheet:
        k.check_silhouette(os.path.join(sheet, "enemy_H.png") if os.path.isdir(sheet) else sheet, 93)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "bronze_yuanbao.glb")
    k.export(path)
    print("   bronze_yuanbao: %.1f KB" % (os.path.getsize(path) / 1024))
    if "preview" in options:
        k.preview(options["preview"] + "bronze_yuanbao")


if __name__ == "__main__":
    build()
