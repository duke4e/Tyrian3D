"""The U-arch (sheet 2 sprites 191-205, 2x2: 24 x 28 pixels; enemies 10 and 12 of episodes 1-5:
MINEMAZE, MINES, TYRIAN, BONUS, HOLES, WINDY, GAUNTLET, TYRIAN X, MACES, ICESECRET, SAVARA and more;
the sky layer, also ground and top in episode 1), polished (2026-10-18; it replaces uarch.py's thin
tube U with a ball). models.cfg: sprite 2 191 uarch yaw=0 roll=frames:16, sprite 2 205 uarch yaw=0
roll=frames:16:ccw.

As the 4x upscale draws it: an arch like a horseshoe, its open end down the screen, bent from a
flat band: face-on (191) the band shows its narrow edge (one pixel of metal in its dark outline:
the sprite's columns 4-6 and 16-18, its top rows 1-3), edge-on (199) its broad face, five pixels of
metal. The bend over the top is bronze, the straight legs steel (their lower part a shade darker), a
dark seam where they meet (row 7) and another across each leg (row 12). Inside it hangs a bronze pod
like a shield, its point down the screen (columns 9-13 of rows 7-13), a dark crease down its middle,
held at mid-height by a short dark strut from each leg (row 10). The sprite's frames turn the whole
thing half a turn about the screen's vertical axis (models.cfg rolls this model with them): the band
has its full depth and the pod its own (a little less, so that edge-on the near leg hides it), and
both faces alike, as the frames show them after half a turn. (The sprite's frames in between are
narrower than anything rigid turning: at 45 degrees it draws the arch 11 pixels across where its
face-on and edge-on frames make 15.)

The sprite centres the arch on column 11, half a pixel left of the sprite's centre; the game rolls
the model about its origin, so the model is centred on it (it turns in place rather than swinging
half a pixel to and fro), half a pixel right of where the sprite draws it. --check compares it both
as built and moved onto the sprite's column 11. Symmetric about x = 0 and about z = 0.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <dir with enemy_2.png,
or the sheet itself> (the silhouette of each frame, the model rolled as models.cfg rolls it),
--preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_sphere_nozzle import smoothstep, split_along  # noqa: E402

SPRITE_X = -0.5  # where the sprite centres the arch (column 11)

# The band's middle line: the legs at x = +-LEG_X from their ends (LEG_BOTTOM, rounded off over
# LEG_CAP) up to BEND_Y, then the bend over the top, a superellipse (power BEND_POWER: 2, the
# upscale's round arch; the sprite's pixels are a little flatter on top) up to BEND_TOP. The
# sprite's legs are columns 5 and 17 (the arch's middle +-6), the top row 2 (y 11.5), the legs' ends
# row 18 (their outline row 19).
LEG_X, LEG_BOTTOM, LEG_CAP = 6.0, -5.75, 0.7
BEND_Y, BEND_TOP, BEND_POWER = 7.0, 11.5, 2.0
# The band's cross-section: half its thickness in the arch's plane (one pixel of metal and most of
# the outline either side), half its depth (the edge-on frame's five pixels of metal and most of
# the outline either side), the superellipse power (flat faces, rounded edges). Over the top of the
# bend it rounds off more and loses a little depth (BEND_SECTION: power and depth there), as the
# edge-on frame draws the bronze cap's top rounded.
BAND_HALF, BAND_DEPTH, BAND_POWER = 1.25, 3.25, 3.0
BEND_SECTION = (2.2, 2.95)
SEAMS = (6.5, 1.5)    # the dark seams across the legs (y): bronze above the first, steel below
SEAM_HALF, SEAM_SINK = 0.24, 0.2  # a seam's half-width along the band, how deep it sinks
BAND_SECTION = 20     # points round the band's cross-section

# The pod: its outline's right half from the top middle down to the tip (most of the way into the
# sprite's outline: columns 9-13 of rows 7-12, three pixels in row 13), its middle for the relief
# grid, half its depth (front and back alike), the crease down the middle of either face.
POD_OUTLINE = [(0.0, 7.75), (1.8, 7.7), (2.8, 7.45), (3.2, 6.8), (3.27, 5.0), (3.25, 3.0), (3.08, 1.9),
               (2.55, 0.9), (1.75, 0.05), (0.85, -0.52), (0.0, -0.85)]
POD_MIDDLE = Vector((0.0, 3.6))
POD_DEPTH = 2.0
POD_CREASE = (0.55, 0.62)  # depth, half-width
POD_CREASE_PAINT = 0.3
POD_RINGS, POD_SEGMENTS = 9, 48

# The struts from the legs' inner faces to the pod's sides (row 10): y, radius at the pod and at
# the leg, the collar where it meets the leg.
STRUT_Y, STRUT_R = 3.5, (0.78, 0.5)
COLLAR = (0.72, 0.3)  # radius, half-length


def superellipse(a, half_u, half_v, power):
    c, s = math.cos(a), math.sin(a)
    return (math.copysign(abs(c) ** (2 / power), c) * half_u, math.copysign(abs(s) ** (2 / power), s) * half_v)


# --- The band -------------------------------------------------------------------------------------

def band_path():
    """The band's middle line from the left leg's end over the top to the right leg's end:
    [(point, tangent, the section's scale (below 1 at the rounded ends), how near the top of the
    bend (0-1))]. The sections run along y on the legs, round the bend in steps of the
    superellipse's angle."""
    def leg_ys():
        ys = [LEG_BOTTOM + LEG_CAP * (1 - d) for d in (0.985, 0.94, 0.84, 0.68, 0.42)]
        ys += [LEG_BOTTOM + LEG_CAP, -3.0, -0.5]
        for seam in sorted(SEAMS):
            ys += [seam - SEAM_HALF - 0.12, seam - SEAM_HALF, seam, seam + SEAM_HALF, seam + SEAM_HALF + 0.12]
        ys += [3.5, 4.8]
        ys = sorted(y for y in ys if y < BEND_Y - 0.05)
        return ys

    def leg_scale(y):
        d = (LEG_BOTTOM + LEG_CAP - y) / LEG_CAP
        return (1 - max(0.0, d) ** 3) ** (1 / 3) if d > 0 else 1.0

    left = [(Vector((-LEG_X, y, 0.0)), Vector((0, 1, 0)), leg_scale(y), 0.0) for y in leg_ys()]
    bend = []
    steps = 28
    for i in range(steps + 1):
        phi = math.pi - math.pi * i / steps  # from the left leg's top over to the right's
        c, s = math.cos(phi), math.sin(phi)
        x = math.copysign(abs(c) ** (2 / BEND_POWER), c) * LEG_X
        y = BEND_Y + abs(s) ** (2 / BEND_POWER) * (BEND_TOP - BEND_Y)
        bend.append(Vector((x, y, 0.0)))
    bend_points = []
    for i, p in enumerate(bend):
        t = (bend[min(i + 1, steps)] - bend[max(i - 1, 0)]).normalized()
        if i == 0:
            t = Vector((0, 1, 0))
        elif i == steps:
            t = Vector((0, -1, 0))
        bend_points.append((p, t, 1.0, math.sin(math.pi * i / steps) ** 2))
    right = [(Vector((LEG_X, p.y, 0.0)), Vector((0, -1, 0)), s, 0.0) for p, _, s, _ in reversed(left)]
    return left + bend_points + right


def seam_inset(y):
    """How far a leg's section sinks at y (the seams' grooves)."""
    return max(SEAM_SINK * max(0.0, 1 - abs(y - seam) / SEAM_HALF) ** 0.7 for seam in SEAMS)


def band_key(y):
    """The material of the band's faces between sections at mean height y (on the legs)."""
    if y > SEAMS[0] + SEAM_HALF:
        return "bronze"
    if any(abs(y - seam) <= SEAM_HALF for seam in SEAMS):
        return "seam"
    return "steel" if y > SEAMS[1] else "steel_low"


def band(mats):
    path = band_path()
    rings = []
    for p, t, scale, top in path:
        out = Vector((-t.y, t.x, 0.0))  # away from the arch's inside
        sink = seam_inset(p.y) if abs(p.x) > LEG_X - 0.01 and p.y < BEND_Y else 0.0
        power = BAND_POWER + (BEND_SECTION[0] - BAND_POWER) * top
        depth = BAND_DEPTH + (BEND_SECTION[1] - BAND_DEPTH) * top
        ring = []
        for i in range(BAND_SECTION):
            a = 2 * math.pi * i / BAND_SECTION
            u, v = superellipse(a, (BAND_HALF - sink) * scale, (depth - sink) * scale, power)
            ring.append(p + out * u + Vector((0, 0, v)))
        rings.append(ring)
    end = lambda x: Vector((x, LEG_BOTTOM, 0.0))
    obj = k.loft("band", rings, mats["bronze"], start_point=end(-LEG_X), end_point=end(LEG_X))
    names = ["bronze"]
    for key in ("steel", "steel_low", "seam"):
        obj.data.materials.append(mats[key])
        names.append(key)
    for poly in obj.data.polygons:
        c = poly.center
        on_leg = abs(abs(c.x) - LEG_X) < BAND_HALF + 0.05 and c.y < BEND_Y
        poly.material_index = names.index(band_key(c.y)) if on_leg else 0
    return k.smooth(obj, 45)


# --- The pod --------------------------------------------------------------------------------------

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


def pod_outline(count):
    """The pod's outline, count points counter-clockwise from the top middle, evenly spaced."""
    right = [Vector(p) for p in POD_OUTLINE]
    left = [Vector((-p.x, p.y)) for p in right[1:-1]]
    loop = [right[0]] + left + [right[-1]] + list(reversed(right[1:-1]))
    dense = catmull_rom_closed(loop)
    lengths = [0.0]
    for a, b in zip(dense, dense[1:] + dense[:1]):
        lengths.append(lengths[-1] + (b - a).length)
    points, j = [], 0
    for i in range(count):
        target = lengths[-1] * i / count
        while lengths[j + 1] < target:
            j += 1
        f = (target - lengths[j]) / max(lengths[j + 1] - lengths[j], 1e-9)
        points.append(dense[j].lerp(dense[(j + 1) % len(dense)], f))
    return points


def edge_distance(edge, origin, a):
    """How far the polygon edge (star-shaped round origin) lies from origin in the direction a."""
    d = Vector((math.cos(a), math.sin(a)))
    best = 0.0
    for p, q in zip(edge, edge[1:] + edge[:1]):
        p = p - origin
        e = (q - origin) - p
        det = d.x * -e.y + d.y * e.x
        if abs(det) < 1e-12:
            continue
        t = (p.x * -e.y + p.y * e.x) / det
        u = (d.x * p.y - d.y * p.x) / det
        if -1e-6 <= u <= 1 + 1e-6 and t > best:
            best = t
    return best


def pod_height(x, y, s):
    """The pod's front face's height at (x, y) (s: 0 at its middle, 1 at its outline): a lens,
    rounded down to the outline, fullest a little above the middle, the crease down its middle."""
    dome = (1 - s * s) ** 0.55
    full = 1.0 - 0.12 * smoothstep(4.0, -0.5, y)  # a little slimmer towards the tip
    rise = POD_DEPTH * dome * full
    width = POD_CREASE[1] * (0.7 + 0.3 * smoothstep(0.0, 7.0, y))
    depth = POD_CREASE[0] * max(0.0, 1 - abs(x) / width) ** 1.2
    return rise - min(depth, 0.5 * rise)


def pod(mats):
    bm = bmesh.new()
    edge = pod_outline(POD_SEGMENTS)
    centre = bm.verts.new((POD_MIDDLE.x, POD_MIDDLE.y, 0.0))
    grid = []
    for i in range(1, POD_RINGS + 1):
        s = (i / POD_RINGS) ** 0.8
        grid.append([bm.verts.new((POD_MIDDLE.x + (e.x - POD_MIDDLE.x) * s, POD_MIDDLE.y + (e.y - POD_MIDDLE.y) * s,
                                   0.0)) for e in edge])
    n = POD_SEGMENTS
    for j in range(n):
        bm.faces.new((centre, grid[0][j], grid[0][(j + 1) % n]))
    for a, b in zip(grid, grid[1:]):
        for j in range(n):
            bm.faces.new((a[j], b[j], b[(j + 1) % n], a[(j + 1) % n]))
    for t in (-POD_CREASE_PAINT, POD_CREASE_PAINT):
        split_along(bm, {v: v.co.x for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    outer = set(grid[-1])
    # The back face: the front mirrored, sharing the outline.
    front_faces = list(bm.faces)
    twin = {}
    for v in list(bm.verts):
        twin[v] = v if v in outer else bm.verts.new(v.co)
    for f in front_faces:
        bm.faces.new([twin[v] for v in reversed(f.verts)]).tag = True
    for v in list(bm.verts):
        r = math.hypot(v.co.x - POD_MIDDLE.x, v.co.y - POD_MIDDLE.y)
        s = 0.0 if r < 1e-9 else min(1.0, r / edge_distance(edge, POD_MIDDLE, math.atan2(v.co.y - POD_MIDDLE.y,
                                                                                         v.co.x - POD_MIDDLE.x)))
        h = pod_height(v.co.x, v.co.y, s) if v not in outer else 0.0
        back = any(f.tag for f in v.link_faces) and v not in outer
        v.co.z = -h if back else h
    keys = ["crease" if abs(f.calc_center_median().x) < POD_CREASE_PAINT else "pod" for f in bm.faces]
    mesh = bpy.data.meshes.new("pod")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("pod", mesh)
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


# --- The struts -----------------------------------------------------------------------------------

def strut(side, mats):
    """A strut from the pod's side out to the leg's inner face, a collar where it meets the leg."""
    x0, x1 = 2.6, LEG_X - BAND_HALF + 0.15
    profile = [(x0, STRUT_R[0]), (x0 + 0.5, STRUT_R[0] * 0.92), (x1 - COLLAR[1] * 2, STRUT_R[1]),
               (x1 - COLLAR[1] * 2 + 0.05, COLLAR[0]), (x1, COLLAR[0])]
    rod = k.lathe("strut", [(x0 - 0.01, 0.0)] + profile + [(x1 + 0.01, 0.0)], mats["strut"], segments=12)
    # Built along +Y: turned to run along x on its side, at the strut's height.
    m = Matrix.Translation((0, STRUT_Y, 0)) @ Matrix.Rotation(math.radians(-90 * side), 4, "Z")
    rod.data.transform(m)
    return k.smooth(rod, 50)


# --- Build ----------------------------------------------------------------------------------------

def materials():
    return {
        "bronze": k.material("uarch_bronze", palette=0x1a, metallic=0.5, roughness=0.3),
        "steel": k.material("uarch_steel", palette=0x0a, metallic=0.45, roughness=0.26),
        "steel_low": k.material("uarch_steel_low", palette=0x09, metallic=0.45, roughness=0.28),
        "seam": k.material("uarch_seam", palette=0x04, metallic=0.3, roughness=0.5),
        "pod": k.material("uarch_pod", palette=0x19, metallic=0.45, roughness=0.28),
        "crease": k.material("uarch_crease", palette=0xa3, metallic=0.3, roughness=0.5),
        "strut": k.material("uarch_strut", palette=0x06, metallic=0.45, roughness=0.32),
    }


def build_model():
    k.reset()
    mats = materials()
    band(mats)
    pod(mats)
    for side in (-1, 1):
        strut(side, mats)


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


def check(sheet):
    """Each frame's silhouette (191, 193, ... 205) against the model rolled as models.cfg rolls it
    (a 16th of a turn a frame), as built and moved onto the sprite's column 11."""
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for f, sprite in enumerate(range(191, 206, 2)):
        for obj in meshes:
            obj.matrix_world = Matrix.Rotation(math.radians(22.5 * f), 4, "Y")
        print("-- 2 %d, rolled %.1f degrees, as built:" % (sprite, 22.5 * f))
        k.check_silhouette(sheet, sprite)
        for obj in meshes:
            obj.matrix_world = Matrix.Translation((SPRITE_X, 0, 0)) @ Matrix.Rotation(math.radians(22.5 * f), 4, "Y")
        print("-- 2 %d, rolled %.1f degrees, on the sprite's column 11:" % (sprite, 22.5 * f))
        k.check_silhouette(sheet, sprite)
    for obj in meshes:
        obj.matrix_world = Matrix.Identity(4)


def build():
    build_model()
    print("triangles:", triangles())
    options = k.args()
    sheet = options.get("check")
    if sheet:
        check(os.path.join(sheet, "enemy_2.png") if os.path.isdir(sheet) else sheet)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.export(os.path.join(outdir, "uarch.glb"))
    if "preview" in options:
        k.preview(options["preview"] + "uarch")


if __name__ == "__main__":
    build()
