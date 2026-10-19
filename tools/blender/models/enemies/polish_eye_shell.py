"""The small blue shell with an eye looking out of it, of GYGES, MISTAKES and CRUSTGATE (sheet G sprite 127, 2x2: a
14 x 12 creature in the 24 x 28 cell; top layer; enemies 190 and 191, its animation 127 127 129 129 129 131 131 131
129 129 129 127), polished (2026-10-19; it replaces wave2_f.py's eye_shell()). models.cfg: sprite g 127 eye_shell
yaw=0, frame g 129 eye_shell_129, frame g 131 eye_shell_131. No other enemy shows these three sprites.

As the 4x upscales draw it: a hood like a snail's shell (rows 8-13, columns 6-19), a smooth blue dome lit at its top
left, its front edge a rolled lip arching over the eye (the light band of row 12) with a shallow groove behind it
(row 11), its sides coming down past the eye as two flaps (columns 6 and 19 of rows 13-15, a dark gap between them
and the eye); under the lip a big eye (rows 13-19, columns 8-17) in a ring of light blue lids: a glass-blue eyeball
with a dark pupil, a white glint at the pupil's upper left and the light gathering in a crescent at its lower right,
as in a marble. The frames move the pupil: in 127 it is in the eye's middle (column 12.5), in 129 a pixel to the
right, in 131 two (the eye glances to the right and back). 129 and 131 draw a black outline round the creature, 127
none: outlines are not geometry. The frame models are the same shell and lids with the eye turned to look where
its frame's pupil is; they share their bounds, so the game, which centres them in height, keeps them in place.

The hood: the upper half of an ellipsoid shell (outer surface blue, the inner one dark), cut open at the front by a
slanting plane (the opening reaches down to the flaps' tips at the sides and up over the eye at the top), a rolled
lip along the cut, a darker groove painted behind the lip, a dark floor inside. The eye: a painted ball (polish_balls)
looking up at the camera and down the screen, inside the opening, its lids a rolled ring round it.

The sprite is symmetric about its columns 12-13 (x 1.0 here): the creature is built about u = 0 and moved there.
Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.

Replaces wave2_f.py's eye_shell() (its @model("eye_shell", "enemy_G", 129) function and the eye_shell lines of the
docstring): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against its sprite in enemy_G.png), --preview <prefix>, --only <name,...>.
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
from polish_balls import Ellipsoid, painted_ball, preview, triangles  # noqa: E402
from polish_sphere_nozzle import split_along  # noqa: E402
from polish_squid_ship import tube  # noqa: E402

AXIS_X = 1.0

# The hood: an ellipsoid shell (outer radii, thickness) standing on z = 0, cut open in front of the plane
# y = CUT_FOOT + CUT_SLOPE * z (the flaps' tips at y = CUT_FOOT on the ground, the lip over the eye higher up and
# further back); the groove painted behind the lip (GROOVE: from, to, measured along y from the cut).
HOOD_CENTRE = Vector((0.0, -1.0, 0.0))
HOOD_RADII = Vector((7.35, 7.55, 7.6))
HOOD_THICKNESS = 0.85
CUT_FOOT, CUT_SLOPE = -2.75, 0.62
GROOVE = (0.75, 1.55)
LIP_RADIUS = 0.62

# The eye: its middle and radii (a little wider than tall, as the sprite's); its lids, a rolled oval round
# LID_LOOK, LID_ANGLES degrees from it across and along.
EYE_CENTRE = Vector((0.0, -2.15, 2.0))
EYE_RADII = Vector((5.1, 4.3, 4.3))
LID_LOOK = Vector((0.0, -0.36, 0.933))
LID_ANGLES = (74.0, 64.0)
LID_RADIUS = 0.68
SOCKET = 7.0            # the eye darker this many degrees inside its lids (the socket's shadow)

# The pupil's place in the top view relative to the eye's middle, per frame (127: the middle, 129: a pixel to
# the right, 131: two); the pupil's and the iris's angular radii round where it looks (degrees).
FRAMES = [("eye_shell", 127, (0.0, -1.15)), ("eye_shell_129", 129, (0.85, -1.05)),
          ("eye_shell_131", 131, (1.75, -0.85))]
PUPIL, IRIS = 12.0, 27.0
# The glint (fixed: the light's, not the eye's): its middle in the top view relative to the eye's middle and its
# radius; the crescent where the light gathers, round CRESCENT_AT (degrees from +X in the top view), its middle
# where the normal's z is CRESCENT_Z.
GLINT, GLINT_SIZE = Vector((-1.3, 0.1)), 1.15
CRESCENT_AT, CRESCENT_SPREAD = -40.0, 38.0
CRESCENT_Z, CRESCENT_WIDTH = 0.42, 0.14


def materials():
    pal = k.level_palette()
    return {
        "shell": k.material("eyeshell_shell", palette=0x3b, metallic=0.3, roughness=0.3),
        "groove": k.material("eyeshell_groove", palette=0x37, metallic=0.3, roughness=0.4),
        "lip": k.material("eyeshell_lip", palette=0x3d, metallic=0.3, roughness=0.26),
        "inner": k.material("eyeshell_inner", palette=0x33, metallic=0.2, roughness=0.6),
        "lids": k.material("eyeshell_lids", palette=0x3c, metallic=0.25, roughness=0.26),
        "socket": k.material("eyeshell_socket", palette=0x36, metallic=0.0, roughness=0.3),
        # The eye: blue glass, glowing a little in its own colours (the slanted camera sees much of it in shade).
        "sclera": k.material("eyeshell_eye", palette=0x3a, metallic=0.0, roughness=0.15, emission=pal[0x3a],
                             emission_strength=0.3),
        "iris": k.material("eyeshell_iris", palette=0x34, metallic=0.0, roughness=0.1, emission=pal[0x35],
                           emission_strength=0.25),
        "pupil": k.material("eyeshell_pupil", palette=0x31, metallic=0.0, roughness=0.08),
        "glint": k.material("eyeshell_glint", palette=0x3e, metallic=0.0, roughness=0.1, emission=pal[0x3e],
                            emission_strength=0.5),
        "crescent": k.material("eyeshell_crescent", palette=0x3d, metallic=0.0, roughness=0.12, emission=pal[0x3d],
                               emission_strength=0.4),
    }


# --- The hood -------------------------------------------------------------------------------------------------

def cut_value(co):
    """How far behind the opening's plane a point is (along y; negative: cut away)."""
    return co.y - (CUT_FOOT + CUT_SLOPE * co.z)


def shell_surface(name, radii, mats, inner):
    """The hood's outer (inner=False) or inner surface: the ellipsoid's upper half behind the cut, its faces cut
    along the opening and the ground; the outer one painted with the groove behind the lip."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4 if inner else 5, radius=1.0)
    for v in bm.verts:
        d = v.co.normalized()
        v.co = HOOD_CENTRE + Vector((d.x * radii.x, d.y * radii.y, d.z * radii.z))
    split_along(bm, {v: cut_value(v.co) for v in bm.verts}, 0.0)
    split_along(bm, {v: v.co.z for v in bm.verts}, 0.0)
    if not inner:
        for t in GROOVE:
            split_along(bm, {v: cut_value(v.co) for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    gone = [f for f in bm.faces if cut_value(f.calc_center_median()) < 0 or f.calc_center_median().z < 0]
    bmesh.ops.delete(bm, geom=gone, context="FACES")
    kinds = []
    for f in bm.faces:
        c = f.calc_center_median()
        kinds.append("inner" if inner else "groove" if GROOVE[0] < cut_value(c) < GROOVE[1] else "shell")
    if inner:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    names = []
    for kind in kinds:
        if mats[kind].name not in names:
            names.append(mats[kind].name)
            mesh.materials.append(mats[kind])
    for poly, kind in zip(mesh.polygons, kinds):
        poly.material_index = names.index(mats[kind].name)
    return k.smooth(obj, 70)


def rim_curve(radii, count=22):
    """Where the cut meets an ellipsoid of the given radii: from the right foot over the top to the left foot."""
    def height_at(z):
        y = CUT_FOOT + CUT_SLOPE * z
        return 1 - ((y - HOOD_CENTRE.y) / radii.y) ** 2 - (z / radii.z) ** 2
    lo, hi = 0.0, radii.z
    for _ in range(50):
        mid = (lo + hi) / 2
        if height_at(mid) > 0:
            lo = mid
        else:
            hi = mid
    z_top = lo
    right = []
    for i in range(count + 1):
        z = z_top * math.sin(0.5 * math.pi * i / count)
        x = radii.x * math.sqrt(max(0.0, height_at(z)))
        right.append(Vector((x, CUT_FOOT + CUT_SLOPE * z, z)))
    left = [Vector((-p.x, p.y, p.z)) for p in reversed(right[:-1])]
    return right + left


def hood(m):
    shell_surface("hood", HOOD_RADII, m, inner=False)
    inner_radii = HOOD_RADII - Vector((HOOD_THICKNESS,) * 3)
    shell_surface("hood_inner", inner_radii, m, inner=True)
    # The lip: a rolled edge along the cut, between the outer and the inner surface.
    outer, inner = rim_curve(HOOD_RADII), rim_curve(inner_radii)
    path = [(a + b) / 2 for a, b in zip(outer, inner)]
    path[0].z = path[-1].z = 0.25
    tube("lip", path, [LIP_RADIUS] * len(path), m["lip"], segments=10)
    # The floor inside (dark), under the eye: the inner surface's foot behind the opening.
    rx, ry = inner_radii.x - 0.1, inner_radii.y - 0.1
    y0 = CUT_FOOT + 0.05
    a0 = math.asin(max(-1.0, min(1.0, (y0 - HOOD_CENTRE.y) / ry)))
    ring = [Vector((HOOD_CENTRE.x + rx * math.cos(a), HOOD_CENTRE.y + ry * math.sin(a), 0.05))
            for a in [a0 + (math.pi - 2 * a0) * i / 32 for i in range(33)]]
    floor = k.mesh_object("floor", ring, [list(range(len(ring)))], m["inner"])
    k.recalc_normals(floor)
    if floor.data.polygons[0].normal.z < 0:
        floor.data.flip_normals()


# --- The eye --------------------------------------------------------------------------------------------------

def look_of(offset):
    """The direction the eye looks in (from its middle), so that the pupil shows `offset` from the eye's middle
    in the top view."""
    dx, dy = offset
    r = EYE_RADII
    d = Vector((dx / r.x, dy / r.y, 0.0))
    d.z = math.sqrt(max(0.0, 1 - d.x * d.x - d.y * d.y))
    return Vector((d.x / r.x, d.y / r.y, d.z / r.z)).normalized()  # the surface's normal there


def eye(m, offset):
    look = look_of(offset)
    shape = Ellipsoid(EYE_CENTRE, EYE_RADII)

    def angle(p, n):
        return math.degrees(n.angle(look))

    def glint(p, n):
        if n.z < 0.3:
            return 0.0
        q = Vector((p.x - EYE_CENTRE.x - GLINT.x, p.y - EYE_CENTRE.y - GLINT.y))
        return math.exp(-(q.length / GLINT_SIZE) ** 2)

    def crescent(p, n):
        if n.z <= 0:
            return 0.0
        a = math.degrees(math.atan2(p.y - EYE_CENTRE.y, p.x - EYE_CENTRE.x))
        off = ((a - CRESCENT_AT + 180) % 360 - 180) / CRESCENT_SPREAD
        return math.exp(-off * off - ((n.z - CRESCENT_Z) / CRESCENT_WIDTH) ** 2)

    lid_axis = LID_LOOK.normalized()
    lid_side = Vector((1.0, 0.0, 0.0))
    lid_up = lid_axis.cross(lid_side).normalized()

    def socket(p, n):
        """How far inside the lids a point is (degrees: its angle from LID_LOOK less the lids' there)."""
        d = (p - EYE_CENTRE)
        d = Vector((d.x / EYE_RADII.x, d.y / EYE_RADII.y, d.z / EYE_RADII.z)).normalized()
        c = d.dot(lid_axis)
        a, b = d.dot(lid_side), d.dot(lid_up)
        t = math.atan2(b, a)
        across, along = (math.radians(v) for v in LID_ANGLES)
        lid = math.atan2(math.hypot(math.sin(across) * math.cos(t), math.sin(along) * math.sin(t)),
                         math.hypot(math.cos(across) * math.cos(t), math.cos(along) * math.sin(t)))
        return math.degrees(lid - math.acos(max(-1.0, min(1.0, c))))

    paint = [
        (lambda p, n: 1.0, (), ("sclera",)),
        (socket, (SOCKET,), ("socket", None)),
        (crescent, (0.45,), (None, "crescent")),
        (angle, (PUPIL, IRIS), ("pupil", "iris", None)),
        (glint, (0.45,), (None, "glint")),
    ]
    painted_ball("eye", shape, paint, m, subdivisions=5, smooth_angle=70)
    # The lids: a rolled oval ring round the eye, lying on its surface.
    axis = LID_LOOK.normalized()
    side = Vector((1.0, 0.0, 0.0))
    up = axis.cross(side).normalized()
    across, along = (math.radians(a) for a in LID_ANGLES)
    points = []
    for i in range(48):
        t = 2 * math.pi * i / 48
        c, s = math.cos(t), math.sin(t)
        a = math.atan2(math.hypot(math.sin(across) * c, math.sin(along) * s),
                       math.hypot(math.cos(across) * c, math.cos(along) * s))
        w = side * c + up * s
        d = (axis * math.cos(a) + w * math.sin(a)).normalized()
        p, n = shape.point(d)
        points.append(p + n * 0.1)
    points.append(points[0])
    return tube("lids", points, [LID_RADIUS] * len(points), m["lids"], segments=8, squash=0.85)


# --- Build ----------------------------------------------------------------------------------------------------

def build_model(offset):
    k.reset()
    m = materials()
    hood(m)
    eye(m, offset)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(Matrix.Translation((AXIS_X, 0.0, 0.0)))


def bounds():
    vs = [obj.matrix_world @ v.co for obj in bpy.context.scene.objects if obj.type == "MESH" for v in obj.data.vertices]
    return [min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)]


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, offset in FRAMES:
        if only is not None and name not in only:
            continue
        build_model(offset)
        used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
        low, high = bounds()
        print("== %s (G %d): %d triangles, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f: %s" % (
            name, sprite, triangles(), len(used), low[0], high[0], low[1], high[1], low[2], high[2],
            ", ".join(sorted(used))))
        if "check" in options:
            k.check_silhouette(os.path.join(options["check"], "enemy_G.png"), sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        if "preview" in options:
            preview(options["preview"] + name, distance=0.6)


if __name__ == "__main__":
    build()
