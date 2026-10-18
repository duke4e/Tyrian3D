"""The ring core (sheet 2 sprites 229-243, 2x2: 24 x 28 pixels; enemies 5 and 11 of episodes 1-4:
MINEMAZE, MINES, TYRIAN, BONUS, HOLES, WINDY, ASSASSIN, GAUNTLET, TYRIAN X, MACES and more; sky,
ground and top layers), polished (2026-10-18; it replaces ringcore.py's two grey arcs round a red
dot, which models.cfg turned whole, core and all). One model per frame, the core fixed and the arcs
at that frame's angle: ringcore (229), ringcore_231, ringcore_233, ... ringcore_243. models.cfg:
sprite 2 229 ringcore yaw=0, sprite 2 243 ringcore yaw=0 (the type that runs the frames
backwards), frame 2 231 ringcore_231 ... frame 2 243 ringcore_243.

As the 4x upscale draws it: a small chrome core like a heart-shaped shield, its point down the
screen (the sprite's columns 9-15 of rows 9-15 in frame 229: seven pixels across its top, straight
sides, a rounded V below), split down the middle by a dark V crease into two bulging lobes, the
crease widest in the notch at the top; a red-orange eye glows in each rounded top corner, an oval
slanted along the corner (palette 0x75-0x79, the hot middle the 0x79 orange of the sprite's corner
pixel) in a dark red socket. Round it two chrome arcs, each a little over 140 degrees of a ring 17
pixels across (the metal two pixels wide in a dark outline), with blunt rounded ends; from frame to
frame they turn a 16th of a turn clockwise (229: left and right; 237: above and below), the core
holding still. The sprite's arcs are light on their inner half and dark on the outer: the tubes'
cross-sections are turned so that their inner half faces up, and take three shades by how steeply
they face (crown, flanks, sides).

The sprite's frames draw core and ring together a pixel up, down, left or right of each other
(their centre at pixel (12, 12) in 229 and 235, (11, 13) in 231, 233 and 243, (12, 13) in 237-241):
the models keep them at their mean, CENTRE, so the core holds still while the arcs turn. --check
compares each frame both as built and moved onto the frame's own centre (FRAMES), which measures
the shape without the jitter.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <dir with enemy_2.png,
or the sheet itself> (the silhouette of each frame), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_sphere_nozzle import smoothstep, split_along  # noqa: E402

CENTRE = Vector((0.0, 0.75))  # the core's and the ring's centre: the mean of the frames' centres

# The frames: (model name, sprite, the arcs' turn in degrees (counter-clockwise; 229 has them left
# and right), the sprite's own centre of core and ring (x, y) for --check).
FRAMES = [
    ("ringcore", 229, 0.0, (0.5, 1.5)),
    ("ringcore_231", 231, -22.5, (-0.5, 0.5)),
    ("ringcore_233", 233, -45.0, (-0.5, 0.5)),
    ("ringcore_235", 235, -67.5, (0.5, 1.5)),
    ("ringcore_237", 237, -90.0, (0.5, 0.5)),
    ("ringcore_239", 239, -112.5, (0.5, 0.5)),
    ("ringcore_241", 241, -135.0, (0.5, 0.5)),
    ("ringcore_243", 243, -157.5, (-0.5, 0.5)),
]

# The arcs: the ring's middle (the sprite's metal spans radii 7.5-9.5, its outline 6.5-10.5), the
# tube's half-width (in plan, most of the way into the outline) and half-height, its
# cross-section's superellipse power, its middle's height. The cross-section is turned ARC_TILT
# degrees about the tube's middle so that its inner half faces up and its outer half rounds away
# down: the sprite's arcs are light on their inner half, dark on the outer. Each arc spans ARC_SPAN
# degrees along the ring's middle (its rounded ends included; the sprite's metal spans about 137,
# its outline 152), the last ARC_CAP pixels of either end rounded off.
RING_RADIUS = 8.5
ARC_HALF_WIDTH, ARC_HALF_HEIGHT, ARC_POWER, ARC_Z = 1.85, 1.2, 2.3, 0.6
ARC_TILT = 18.0
ARC_SPAN = 148.0
ARC_CAP = 1.3
ARC_BANDS = (0.9, 0.62)  # faces whose normal's z is below these take the flank's and the side's colour
ARC_STEPS, ARC_SECTION = 22, 16  # sections along an arc (between its ends), points round a section

# The core's outline relative to CENTRE, its right half from the top middle down to the bottom
# tip (most of the way into the sprite's dark outline: columns 8-16 of rows 8-16 in frame 229),
# smoothed through. A little heart-shaped: a dip in the top's middle, the sides rounding in
# towards the tip, as the upscale draws it.
OUTLINE = [(0.0, 4.08), (0.9, 4.2), (1.9, 4.25), (2.9, 4.15), (3.72, 3.85), (4.17, 3.2), (4.3, 2.0),
           (4.27, 0.25), (4.1, -0.9), (3.5, -1.98), (2.5, -2.98), (1.38, -3.84), (0.0, -4.35)]
CORE_INSET = 0.32       # the top's edge, inside the outline (the rim rounds over from it)
CORE_EDGE_Z = 1.7       # the top's edge
CORE_RISE = 2.4         # the top: how much higher than its edge at the lobes
CORE_BOTTOM_Z = -0.9
LOBES = (2.0, 0.6, 0.32)  # the lobes either side of the crease: x, y, how much of the rise they make
CREASE = (0.9, 0.62)    # the V crease down the middle: depth, half-width (at the top; narrower below)
CREASE_PAINT = (0.3, 0.5)  # its dark line: |x| below this (at the bottom, at the top)
# The eyes in the top corners: centre (the left one; the right one mirrored), half-length,
# half-width, the long axis's angle (degrees: along the corner), the socket's depth, how much the
# lens bulges in it, the socket's rim (in units of the eye's size).
EYE = (-2.72, 2.78)
EYE_SIZE = (1.25, 0.66)
EYE_ANGLE = 40.0
EYE_DEPTH, LENS_BULGE, SOCKET = 0.42, 0.3, 1.28
EYE_BANDS = (0.45, 0.8, 1.0)  # the lens's colours change at these (hot middle, middle, rim)
GRID_RINGS, GRID_SEGMENTS = 8, 48


# --- The arcs -------------------------------------------------------------------------------------

def arc_section(t, scale):
    """The tube's cross-section at angle t (radians) along the ring, scaled (the rounded ends),
    turned so that its inner half faces up."""
    radial = Vector((math.cos(t), math.sin(t), 0.0))
    up = Vector((0.0, 0.0, 1.0))
    middle = Vector((CENTRE.x, CENTRE.y, ARC_Z)) + radial * RING_RADIUS
    lean_c, lean_s = math.cos(math.radians(ARC_TILT)), math.sin(math.radians(ARC_TILT))
    points = []
    for i in range(ARC_SECTION):
        a = 2 * math.pi * i / ARC_SECTION
        c, s = math.cos(a), math.sin(a)
        u = math.copysign(abs(c) ** (2 / ARC_POWER), c) * ARC_HALF_WIDTH * scale
        v = math.copysign(abs(s) ** (2 / ARC_POWER), s) * ARC_HALF_HEIGHT * scale
        points.append(middle + radial * (u * lean_c + v * lean_s) + up * (v * lean_c - u * lean_s))
    return points


def arc(name, mid_degrees, mats):
    """One arc, centred on mid_degrees (counter-clockwise from +x): the tube along the ring, its
    ends rounded off (blunt: a superellipse of power 3 along the arc)."""
    half = math.radians(ARC_SPAN / 2)
    cap = ARC_CAP / RING_RADIUS
    mid = math.radians(mid_degrees)
    end_depths = [0.0, 0.42, 0.68, 0.84, 0.94, 0.985]  # into a rounded end, as a fraction of it

    def cap_scale(d):
        return (1 - d ** 3) ** (1 / 3)

    rings = []
    for d in reversed(end_depths[1:]):  # the start's rounded end, towards the body
        rings.append(arc_section(mid - half + cap * (1 - d), cap_scale(d)))
    for i in range(ARC_STEPS + 1):
        rings.append(arc_section(mid - half + cap + (2 * half - 2 * cap) * i / ARC_STEPS, 1.0))
    for d in end_depths[1:]:
        rings.append(arc_section(mid + half - cap * (1 - d), cap_scale(d)))
    tip = lambda t: Vector((CENTRE.x, CENTRE.y, ARC_Z)) + Vector((math.cos(t), math.sin(t), 0.0)) * RING_RADIUS
    obj = k.loft(name, rings, mats["arc"], start_point=tip(mid - half), end_point=tip(mid + half))
    obj.data.materials.append(mats["arc_flank"])
    obj.data.materials.append(mats["arc_side"])
    for poly in obj.data.polygons:
        poly.material_index = sum(poly.normal.z < band for band in ARC_BANDS)
    return k.smooth(obj, 60)


# --- The core -------------------------------------------------------------------------------------

def catmull_rom_closed(points, per_segment=12):
    out = []
    n = len(points)
    for i in range(n):
        p0, p1, p2, p3 = points[i - 1], points[i], points[(i + 1) % n], points[(i + 2) % n]
        for s in range(per_segment):
            t = s / per_segment
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    return out


def outline(count):
    """The core's outline relative to CENTRE: count points counter-clockwise from the top middle,
    evenly spaced along it, and their outward normals."""
    right = [Vector(p) for p in OUTLINE]
    left = [Vector((-p.x, p.y)) for p in right[1:-1]]
    loop = [right[0]] + left + [right[-1]] + list(reversed(right[1:-1]))
    dense = catmull_rom_closed(loop)
    lengths = [0.0]
    for a, b in zip(dense, dense[1:] + dense[:1]):
        lengths.append(lengths[-1] + (b - a).length)
    total = lengths[-1]
    points = []
    j = 0
    for i in range(count):
        target = total * i / count
        while lengths[j + 1] < target:
            j += 1
        f = (target - lengths[j]) / max(lengths[j + 1] - lengths[j], 1e-9)
        points.append(dense[j].lerp(dense[(j + 1) % len(dense)], f))
    normals = []
    for i in range(count):
        t = (points[(i + 1) % count] - points[i - 1]).normalized()
        normals.append(Vector((t.y, -t.x)))
    return points, normals


def eye_frame(x):
    """The eye on x's side: its centre and its long axis (unit vectors along and across it)."""
    side = 1 if x > 0 else -1
    a = math.radians(EYE_ANGLE if side < 0 else 180 - EYE_ANGLE)
    along = Vector((math.cos(a), math.sin(a)))
    return Vector((abs(EYE[0]) * side, EYE[1])), along, Vector((-along.y, along.x))


def eye_q(x, y):
    """The elliptical distance from the nearer eye's centre (1 on the lens's edge)."""
    centre, along, across = eye_frame(x)
    d = Vector((x, y)) - centre
    return math.hypot(d.dot(along) / EYE_SIZE[0], d.dot(across) / EYE_SIZE[1])


def surface(x, y, s):
    """The top's height at (x, y) (relative to CENTRE), s: 0 in the middle, 1 at the top's edge:
    a dome with two lobes either side of the crease, the eyes sunk into its top corners."""
    dome = (1 - s * s) ** 0.75
    lx, ly, bulge = LOBES
    lobe = math.exp(-(((abs(x) - lx) / 1.8) ** 2 + ((y - ly) / 3.0) ** 2))
    rise = CORE_RISE * dome * (1 - bulge + bulge * lobe)
    # The V crease, wider and deeper at the top, never below the top's edge.
    width = CREASE[1] * (0.6 + 0.4 * smoothstep(-4.0, 3.5, y))
    depth = CREASE[0] * (0.7 + 0.3 * smoothstep(-4.0, 3.5, y)) * max(0.0, 1 - abs(x) / width) ** 1.2
    z = CORE_EDGE_Z + rise - min(depth, 0.85 * rise)
    q = eye_q(x, y)
    if q < SOCKET:
        if q < 1.0:
            z += -EYE_DEPTH + LENS_BULGE * math.sqrt(max(0.0, 1 - q * q))
        else:
            z -= EYE_DEPTH * smoothstep(SOCKET, 1.0, q)
    return z


def crease_paint(y):
    return CREASE_PAINT[0] + (CREASE_PAINT[1] - CREASE_PAINT[0]) * smoothstep(-4.0, 3.5, y)


def region(x, y):
    q = eye_q(x, y)
    if q < EYE_BANDS[0]:
        return "eye_hot"
    if q < EYE_BANDS[1]:
        return "eye"
    if q < EYE_BANDS[2]:
        return "eye_rim"
    if q < SOCKET:
        return "socket"
    if abs(x) < crease_paint(y) and y < 3.75:
        return "crease"
    return "body"


def edge_distance(edge, a):
    """How far the top's edge (a star-shaped polygon round CENTRE) lies in the direction a."""
    d = Vector((math.cos(a), math.sin(a)))
    best = 0.0
    for p, q in zip(edge, edge[1:] + edge[:1]):
        e = q - p
        det = d.x * -e.y + d.y * e.x  # solve t * d = p + u * e
        if abs(det) < 1e-12:
            continue
        t = (p.x * -e.y + p.y * e.x) / det
        u = (d.x * p.y - d.y * p.x) / det
        if -1e-6 <= u <= 1 + 1e-6 and t > best:
            best = t
    return best


def core(mats):
    """The core: its top a relief on a polar grid inside the outline (CORE_INSET in), the rim
    rounding over from it to the outline and in underneath, closed below."""
    bm = bmesh.new()
    part = bm.faces.layers.int.new("part")  # 1 on the rim and the bottom
    points, normals = outline(GRID_SEGMENTS)
    edge = [p - nn * CORE_INSET for p, nn in zip(points, normals)]
    centre = bm.verts.new((CENTRE.x, CENTRE.y, 0.0))
    grid = []
    for i in range(1, GRID_RINGS + 1):
        s = (i / GRID_RINGS) ** 0.85
        grid.append([bm.verts.new((CENTRE.x + e.x * s, CENTRE.y + e.y * s, 0.0)) for e in edge])
    n = GRID_SEGMENTS
    for j in range(n):
        bm.faces.new((centre, grid[0][j], grid[0][(j + 1) % n]))
    for a, b in zip(grid, grid[1:]):
        for j in range(n):
            bm.faces.new((a[j], b[j], b[(j + 1) % n], a[(j + 1) % n]))
    # The colours' borders, cut into the flat grid first so that they run smoothly: the eyes'
    # bands and sockets, the crease's line.
    for t in EYE_BANDS + (SOCKET,):
        split_along(bm, {v: eye_q(v.co.x - CENTRE.x, v.co.y - CENTRE.y) for v in bm.verts}, t)
    for t in (-1.0, 1.0):
        split_along(bm, {v: (v.co.x - CENTRE.x) / crease_paint(v.co.y - CENTRE.y) for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    top = list(bm.verts)
    outer = grid[-1]

    # The rim, rounding over from the top's edge out to the widest point (the outline) and in
    # underneath, and the bottom.
    rim_profile = [(-0.17, -0.12), (-0.05, -0.38), (0.0, -0.78), (-0.06, -1.3), (-0.3, -1.85),
                   (-0.85, CORE_BOTTOM_Z - CORE_EDGE_Z)]
    previous = outer
    for d, dz in rim_profile:
        ring = [bm.verts.new((CENTRE.x + p.x + nn.x * d, CENTRE.y + p.y + nn.y * d, CORE_EDGE_Z + dz))
                for p, nn in zip(points, normals)]
        for j in range(n):
            bm.faces.new((previous[j], ring[j], ring[(j + 1) % n], previous[(j + 1) % n]))[part] = 1
        previous = ring
    bottom = bm.verts.new((CENTRE.x, CENTRE.y - 0.2, CORE_BOTTOM_Z - 0.15))
    for j in range(n):
        bm.faces.new((previous[j], bottom, previous[(j + 1) % n]))[part] = 1

    # The top's relief: s from where the vertex lies between the middle and the top's edge.
    for v in top:
        x, y = v.co.x - CENTRE.x, v.co.y - CENTRE.y
        r = math.hypot(x, y)
        s = 0.0 if r < 1e-9 else min(1.0, r / edge_distance(edge, math.atan2(y, x)))
        v.co.z = surface(x, y, s)

    keys = []
    for f in bm.faces:
        c = f.calc_center_median()
        keys.append("rim" if f[part] else region(c.x - CENTRE.x, c.y - CENTRE.y))
    mesh = bpy.data.meshes.new("core")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("core", mesh)
    bpy.context.scene.collection.objects.link(obj)
    names = []
    for key in keys:
        if key not in names:
            names.append(key)
            mesh.materials.append(mats[key])
    for poly, key in zip(mesh.polygons, keys):
        poly.material_index = names.index(key)
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


# --- Build ----------------------------------------------------------------------------------------

def materials():
    glow = k.level_palette()
    return {
        "arc": k.material("ringcore_arc", palette=11, metallic=0.55, roughness=0.16),
        "arc_flank": k.material("ringcore_arc_flank", palette=7, metallic=0.55, roughness=0.2),
        "arc_side": k.material("ringcore_arc_side", palette=4, metallic=0.5, roughness=0.3),
        "body": k.material("ringcore_core", palette=11, metallic=0.38, roughness=0.2),
        "crease": k.material("ringcore_crease", palette=3, metallic=0.3, roughness=0.45),
        "rim": k.material("ringcore_rim", palette=5, metallic=0.5, roughness=0.25),
        "socket": k.material("ringcore_socket", palette=0x72, metallic=0.1, roughness=0.5),
        "eye_rim": k.material("ringcore_eye_rim", palette=0x75, roughness=0.3, emission=glow[0x75],
                              emission_strength=0.5),
        "eye": k.material("ringcore_eye", palette=0x77, roughness=0.25, emission=glow[0x77], emission_strength=0.7),
        "eye_hot": k.material("ringcore_eye_hot", palette=0x79, roughness=0.25, emission=glow[0x79],
                              emission_strength=0.9),
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


def check(sheet, sprite, own_centre):
    """The frame's silhouette against the sprite's: as built, then moved onto the sprite's own
    centre of core and ring for this frame (the sprite's jitter left out)."""
    print("-- as built:")
    k.check_silhouette(sheet, sprite)
    shift = Vector((own_centre[0] - CENTRE.x, own_centre[1] - CENTRE.y, 0.0))
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for obj in meshes:
        obj.location += shift
    print("-- on the frame's own centre (%.1f, %.1f):" % own_centre)
    score = k.check_silhouette(sheet, sprite)
    for obj in meshes:
        obj.location -= shift
    return score


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    sheet = options.get("check")
    if sheet and os.path.isdir(sheet):
        sheet = os.path.join(sheet, "enemy_2.png")
    for name, sprite, turn, own_centre in FRAMES:
        k.reset()
        mats = materials()
        core(mats)
        arc("arc_a", 180.0 + turn, mats)
        arc("arc_b", turn, mats)
        print("== %s (2 %d): %d triangles, %d materials" % (name, sprite, triangles(), len(
            {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials})))
        if sheet:
            check(sheet, sprite, own_centre)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        k.export(os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
