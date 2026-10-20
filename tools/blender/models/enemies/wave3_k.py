"""Batch K of wave 3: the remaining enemies of sheet I (SAVARA, SAVARA V, SAVARA Y), a large object the game
draws from several 2x2 sprites, built whole and cut into the sprites' pieces (models.cfg: origin, yaw=0,
authored as the sprites look). (SAVARA's grey airship, zeppelin_<sprite>: polish_airship.py.)

- redwing_<sprite> (I 201, 203, 237, 239, 241, 243, 278): the red and grey jet fighter, 96 x 80
  pixels, nose down the screen: a red beak with intakes at its cheeks, two black canopies at the
  wing roots, a grey spine, straight wings with red panels and vents, two engine nacelles on a
  tailplane with fins at its tips and a fin in the middle (about 0 to 18 pixels high).

usage: Blender -b --factory-startup -P wave3_k.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole <prefix>]
--only takes object names (redwing) or piece names; --whole renders the whole objects
(<prefix><object>_top.png, _3q.png) instead of exporting.
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
import wave1_d_shapes as sh  # noqa: E402
import wave2_f_kit as w  # noqa: E402
from wave2_f_kit import pal  # noqa: E402

ENEMIES = w.ENEMIES


# --- Helpers ---------------------------------------------------------------------------------------

def tube(name, points, radius, mat, segments=12, squash=1.0, smooth_angle=60):
    """A tube through 3D points with rounded ends; radius a number or one per point; squash scales
    its cross-section towards the up direction (a band taller or flatter than wide)."""
    pts = [Vector(p) for p in points]
    radii = radius if isinstance(radius, (list, tuple)) else [radius] * len(pts)
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        up = side.cross(tangent).normalized()
        rings.append([p + (side * math.cos(2 * math.pi * j / segments) +
                           up * math.sin(2 * math.pi * j / segments) * squash) * radii[i] for j in range(segments)])
    t0, t1 = (pts[1] - pts[0]).normalized(), (pts[-1] - pts[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=pts[0] - t0 * radii[0] * 0.6, end_point=pts[-1] + t1 * radii[-1] * 0.6)
    return k.smooth(obj, smooth_angle)


def lathe_y(name, profile, mat, x, z, segments=24, squash=1.0, smooth_angle=50):
    """A turned part along Y: profile is (y, radius) pairs in increasing y."""
    return k.smooth(k.lathe(name, profile, mat, segments=segments, axis_x=x, axis_z=z, squash=squash), smooth_angle)


def paint(obj, fn):
    """Gives each face the material fn(face centre, normal) returns (None: keep)."""
    mats = list(obj.data.materials)
    for poly in obj.data.polygons:
        mat = fn(poly.center, poly.normal)
        if mat is None:
            continue
        if mat.name not in [m.name for m in mats]:
            obj.data.materials.append(mat)
            mats.append(mat)
        poly.material_index = [m.name for m in mats].index(mat.name)
    return obj


def cut_lines(obj, xs=(), ys=()):
    """Cuts the faces of obj along the planes x = each of xs and y = each of ys (so that painting
    by position gets straight borders)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for value, normal in [(x, (1, 0, 0)) for x in xs] + [(y, (0, 1, 0)) for y in ys]:
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        co = (value, 0, 0) if normal[0] else (0, value, 0)
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=normal)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def mirror(objects, axis_x):
    return w.mirror(objects, axis_x)


def triangles(obj):
    return sum(len(p.vertices) - 2 for p in obj.data.polygons)


def planar(obj, degrees=1.0):
    """Merges nearly flat stretches into larger faces (keeping material borders), then
    triangulates: flat parts cost few triangles."""
    mod = obj.modifiers.new("planar", "DECIMATE")
    mod.decimate_type = "DISSOLVE"
    mod.angle_limit = math.radians(degrees)
    mod.delimit = {"MATERIAL"}
    sh.apply_modifiers(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


# --- The red fighter (I 201 ... 278) --------------------------------------------------------------
# The whole plane in pixel coordinates of its 96 x 84 block of the sheet (columns 96-191, rows
# 140-223): x = column - 144, y = 182 - row (pixel edges); symmetric about column 144's middle.

PX = 0.5      # its axis
PZ = 7.5      # the fuselage's axis height
PSQ = 0.7     # the fuselage's height over its width

FUSELAGE = [(-41.0, 0.01), (-40.3, 0.9), (-38.5, 1.8), (-36.5, 2.8), (-34.5, 3.7), (-32.5, 4.5), (-30.5, 5.3),
            (-28.0, 6.4), (-25.0, 6.9), (-21.0, 7.2), (-16.5, 7.6), (-13.5, 8.8), (-10.0, 10.1), (-5.0, 10.6),
            (5.0, 10.6), (12.0, 10.4), (15.5, 9.6), (18.0, 7.8), (20.5, 6.4), (24.0, 6.0), (30.0, 5.8), (33.5, 5.0),
            (35.5, 3.6), (36.6, 1.8), (37.0, 0.01)]
_FUSELAGE_SAMPLES = None


def fuselage_radius(y):
    global _FUSELAGE_SAMPLES
    if _FUSELAGE_SAMPLES is None:
        _FUSELAGE_SAMPLES = k.profile(FUSELAGE, 0.25)
    s = _FUSELAGE_SAMPLES
    if y <= s[0][0] or y >= s[-1][0]:
        return 0.0
    for (y0, r0), (y1, r1) in zip(s, s[1:]):
        if y0 <= y <= y1:
            return r0 + (r1 - r0) * (y - y0) / max(y1 - y0, 1e-6)
    return 0.0


def fuselage_top(x, y):
    r = fuselage_radius(y)
    d = abs(x - PX)
    if r <= 0 or d >= r:
        return PZ
    return PZ + PSQ * r * math.sqrt(1 - (d / r) ** 2)


def yz_plate(name, outline, x, thickness, mat, bevel=0.3, cant=0.0):
    """A vertical plate (a fin): outline [(y, z), ...] counter-clockwise, `thickness` wide in x
    around x, leaning outwards by `cant` degrees (positive: its top towards +x)."""
    plate = k.slab(name, outline, -thickness / 2, thickness / 2, mat, bevel_width=bevel)
    sh.apply_modifiers(plate)
    base_z = min(z for _, z in outline)
    swap = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))  # (a, b, c) -> (c, a, b)
    plate.data.transform(Matrix.Translation((x, 0, base_z)) @ Matrix.Rotation(math.radians(-cant), 4, "Y") @
                         Matrix.Translation((0, 0, -base_z)) @ swap)
    k.recalc_normals(plate)
    return k.smooth(plate, 35)


def redwing_whole():
    """The whole fighter (see the module's docstring)."""
    red = pal("rw_red", 70, metallic=0.4, roughness=0.32)
    red_light = pal("rw_red_light", 73, metallic=0.4, roughness=0.28)
    red_dark = pal("rw_red_dark", 67, metallic=0.4, roughness=0.4)
    grey = pal("rw_grey", 6, metallic=0.6, roughness=0.32)
    grey_light = pal("rw_grey_light", 9, metallic=0.6, roughness=0.28)
    dark = pal("rw_dark", 2, metallic=0.3, roughness=0.55)
    glass = pal("rw_glass", 1, metallic=0.6, roughness=0.08)

    # The fuselage: red, its tail grey; a grey spine along its back from the tail to the canopies.
    body = lathe_y("fuselage", k.profile(FUSELAGE, 0.8), red, PX, PZ, segments=36, squash=PSQ, smooth_angle=60)
    paint(body, lambda c, n: grey if c.y > 17.5 else None)
    spine = [(PX, y, fuselage_top(PX, y) - 0.9) for y in [36.0 - i * 1.5 for i in range(27)]]
    tube("spine", spine, [min(3.4, 0.55 * fuselage_radius(y) + 0.4) for _, y, _ in spine], grey_light, segments=14,
         squash=0.55)
    # Slats on the red sides behind the canopies.
    for side in (-1, 1):
        for i, y in enumerate((14.8, 12.4, 10.0, 7.6, 5.2)):
            pts = []
            for j in range(6):
                d = 4.4 + 5.4 * j / 5
                x = PX + side * d
                pts.append((x, y, fuselage_top(x, y) + 0.05))
            tube(f"slat{side}{i}", pts, 0.42, red_dark, segments=6, squash=0.8)
    # The beak: a ridge along its top, a collar near its tip, the cheeks' intakes.
    ridge = [(PX, y, fuselage_top(PX, y) - 0.25) for y in [-13.0 - i * 1.5 for i in range(17)]]
    tube("ridge", ridge, [max(0.5, min(1.3, 0.2 * fuselage_radius(y))) for _, y, _ in ridge], red_light, segments=10,
         squash=0.7)
    for i, (y, r, length) in enumerate(((-27.2, 7.4, 1.8),)):
        w.lathe_axis(f"collar{i}", [(0.0, r - 0.7), (0.3, r), (length - 0.3, r), (length, r - 0.7)], red_dark,
                     (PX, y, PZ), (0, -1, 0), 32, squash=PSQ)
    for side in (-1, 1):
        x = side * 8.1
        lathe_y(f"cheek{side}", [(-23.6, 0.01), (-23.4, 1.2), (-22.6, 1.9), (-15.0, 1.9), (-13.4, 1.4), (-12.8, 0.01)],
                red_dark, x, PZ + 1.6, 16, squash=1.3)
        w.sphere(f"cheek_intake{side}", (x, -23.3, PZ + 1.6), (1.3, 0.5, 1.8), dark, 12, 6)
    # The canopies at the wing roots, set in red frames, and the small dark window between them.
    for side in (-1, 1):
        x = PX + side * 8.2
        z = fuselage_top(x, -7.0)
        w.sphere(f"canopy_frame{side}", (PX + side * 8.4, -6.8, z - 1.4), (5.5, 7.2, 3.6), red, 28, 14)
        w.sphere(f"canopy{side}", (PX + side * 8.0, -6.6, z + 0.4), (3.7, 5.3, 2.8), glass, 28, 14)
    w.sphere("window", (PX, -1.0, fuselage_top(PX, -1.0) - 0.3), (3.6, 3.0, 1.9), glass, 20, 10)

    # The wings: straight trailing edges, the leading edges swept near the roots; grey with red
    # panels and vents, a little dihedral.
    wing_l = [(-43.0, 13.0), (-8.0, 13.0), (-8.0, -14.0), (-13.0, -14.0), (-14.5, -12.5), (-15.0, -9.0), (-33.0, 0.0),
              (-41.0, 0.0), (-44.5, 1.5), (-46.0, 4.5), (-46.0, 9.5), (-45.0, 12.0)]
    wing = sh.inflate("wing", [wing_l], grey, sh.pillow_profile(0.75, 1.3), bottom=1.0, base=0.0, spacing=0.6)
    for v in wing.data.vertices:
        d = max(0.0, abs(v.co.x - PX) - 10.0)
        v.co.z = v.co.z * (1.0 - 0.35 * d / 36.0) + 5.6 + 0.06 * d
    xs = [-39, -38, -37, -36, -35, -34, -33, -32, -29, -20]
    cut_lines(wing, xs=xs, ys=[7.0, 12.0, 1.0, 4.0])
    stripes = [(-39, -38), (-37, -36), (-35, -34), (-33, -32)]

    def wing_paint(c, n):
        if n.z < 0.25:
            return None
        if -29 <= c.x <= -20:
            return red
        if 7.0 <= c.y <= 12.0 and any(a <= c.x <= b for a, b in stripes):
            return red
        if 1.0 <= c.y <= 4.0 and (-38 <= c.x <= -37 or -34 <= c.x <= -32):
            return red
        return None
    paint(wing, wing_paint)
    k.smooth(wing, 50)
    # Panel lines: the grey H by the root and the edge of the red panel.
    lines = []
    for name, path in (("hline_a", [(-18.6, 12.0), (-18.6, -3.4)]), ("hline_b", [(-13.6, 12.0), (-13.6, -7.4)]),
                       ("hline_c", [(-18.6, 5.0), (-13.6, 5.0)])):
        pts = [(x, y, 0.0) for x, y in path]
        pts = [(x, y, sh.surface_z(wing, x, y, 7.0) - 0.12) for x, y, _ in w.catmull(pts, 0.8)]
        lines.append(tube(name, pts, 0.3, dark, segments=6, squash=0.7))
    mirror([wing] + lines, PX)

    # The tail: a tailplane with an engine nacelle on each side (grey on top, red at the sides, a
    # red intake at the front), a small fin at each tip and a fin on the fuselage's back.
    tail = [(-23.4, 32.0), (-3.0, 32.0), (-3.0, 23.4), (-23.4, 23.4)]
    plane = sh.inflate("tailplane", [tail], grey, sh.pillow_profile(0.55, 0.9), bottom=1.0, base=PZ - 0.4,
                       spacing=0.6)
    k.smooth(plane, 50)
    nac_x, nac_z = -12.4, PZ + 0.8
    nacelle = [
        lathe_y("nacelle", [(19.6, 0.01), (19.8, 2.4), (21.0, 3.4), (30.0, 3.6), (32.6, 3.2), (34.4, 2.2), (35.2, 1.0),
                            (35.4, 0.01)], grey_light, nac_x, nac_z + 0.6, 24),
        lathe_y("nacelle_lip", [(19.4, 3.0), (19.7, 3.9), (22.4, 4.0), (22.8, 3.4)], red, nac_x, nac_z + 0.6, 24),
        w.sphere("nacelle_intake", (nac_x, 19.5, nac_z + 0.6), (2.5, 0.5, 2.5), dark, 14, 6),
    ]
    for side in (-1, 1):
        nacelle.append(lathe_y(f"nacelle_side{side}", [(21.4, 0.01), (21.8, 1.6), (23.0, 2.1), (30.4, 2.1),
                                                       (32.2, 1.4), (32.8, 0.01)], red, nac_x + side * 4.7, nac_z,
                               16, squash=1.3))
    tip_fin = yz_plate("tip_fin", [(24.2, PZ), (31.6, PZ), (35.4, PZ + 6.0), (33.4, PZ + 6.4), (27.0, PZ + 2.8)],
                       -20.6, 2.8, grey, bevel=0.4, cant=-15.0)
    mirror([plane, tip_fin] + nacelle, 0.25)
    yz_plate("dorsal_fin", [(20.0, PZ + 5.0), (33.0, PZ + 3.0), (38.8, PZ + 10.0), (36.4, PZ + 10.6),
                            (26.0, PZ + 7.6)], PX, 2.4, grey_light, bevel=0.4)


REDWING_PIECES = [  # (sprite, x0, x1, y0, y1)
    (201, -24, 0, 14, 42), (203, 0, 24, 14, 42),
    (237, -48, -24, -14, 14), (239, -24, 0, -14, 14), (241, 0, 24, -14, 14), (243, 24, 48, -14, 14),
    (278, -12, 12, -42, -14),
]


# --- Main ------------------------------------------------------------------------------------------

OBJECTS = {  # name: (builder, whole size in pixels, sheet, pieces, extra views for --whole)
    "redwing": (redwing_whole, (96, 84), "enemy_I", REDWING_PIECES,
                (("side", (-200, -40, 25), (0, 0, 7)), ("front", (40, -120, 70), (0, -5, 6)))),
}


def clear_extras():
    for obj in list(bpy.context.scene.objects):
        if obj.type != "MESH":
            bpy.data.objects.remove(obj)


def build(builder):
    k.reset()
    builder()
    w.bake()
    for obj in w.meshes():
        planar(obj, 0.6)


def look_from(name, location, target, lens=50):
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    cam.data.lens = lens
    bpy.context.scene.collection.objects.link(cam)
    cam.location = Vector(location)
    cam.rotation_euler = (Vector(target) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    return cam


def render_whole(prefix, name, size, views=()):
    """The whole object: a top view framed like its sprites, a three-quarter view and the views
    given as (suffix, camera location, target)."""
    bpy.context.scene.view_settings.view_transform = "Standard"
    k.preview(prefix + name, size, scale=6)
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = 900, 900
    s = max(size) / 36
    for suffix, location, target in (("3q", (38 * s, -48 * s, 42 * s), (0, 0, 0)),) + tuple(views):
        scene.camera = look_from(suffix, location, target)
        scene.render.filepath = f"{prefix}{name}_{suffix}.png"
        bpy.ops.render.render(write_still=True)


def main():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for oname, (builder, size, sheet, pieces, views) in OBJECTS.items():
        names = {f"{oname}_{p[0]}" for p in pieces}
        if only and oname not in only and not names & only:
            continue
        build(builder)
        print(f"=== {oname}: {sum(triangles(o) for o in w.meshes())} triangles whole")
        if "whole" in options:
            render_whole(options["whole"], oname, size, views)
            continue
        whole = [(obj.name, obj.data) for obj in w.meshes()]
        for obj in w.meshes():
            bpy.data.objects.remove(obj)
        for sprite, x0, x1, y0, y1 in pieces:
            name = f"{oname}_{sprite}"
            if only and oname not in only and name not in only:
                continue
            objs = []
            for oname_, data in whole:
                obj = bpy.data.objects.new(oname_, data.copy())
                bpy.context.scene.collection.objects.link(obj)
                objs.append(obj)
            kept = w.piece(objs, x0, x1, y0, y1)
            total = sum(triangles(o) for o in kept)
            print(f"--- {name}: {total} triangles")
            if "stats" in options:
                for obj in sorted(kept, key=triangles, reverse=True)[:6]:
                    print(f"    {obj.name}: {triangles(obj)}")
            if "check" in options:
                k.check_silhouette(os.path.join(options["check"], sheet + ".png"), [sprite], True)
            k.export(os.path.join(ENEMIES, name + ".glb"))
            if "preview" in options:
                bpy.context.scene.view_settings.view_transform = "Standard"
                k.preview(options["preview"] + name, (24, 28))
            clear_extras()
            for obj in list(w.meshes()):
                bpy.data.objects.remove(obj)


if __name__ == "__main__":
    main()
