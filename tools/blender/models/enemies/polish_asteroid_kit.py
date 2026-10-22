"""Helpers shared by round 37's polished models of the asteroid levels (polish_roof_hangar.py, polish_block_parts.py,
polish_tan_launcher.py, polish_seeker_mine.py, polish_bronze_beetle.py, polish_ore_hauler.py, polish_asteroid_craters.py).
Not a model script itself.

Every object is modelled in the picture's plane (x, y as its sprites draw it, z up towards the camera) and then sheared
along the game camera's line of sight (y - z tan 20, the normals with it: polish_gyges_wall.shear_to_camera), so that the
camera sees every point where the sprites draw it and whatever stands higher in the plane covers what lies under it, as
the game's draw order does. Objects of several sprites are built whole in the plane and cut along their sprites' edges
(x and y planes of the picture: polish_coral_manta.cut, the cuts capped in the part's inside colour; thin painted decals
are clipped without caps) before the shear, so each piece holds what its sprite draws; each piece is then moved so that
its sprite's middle is its origin.

The parts are solids built from explicit vertices (prisms, lofts from explicit rings, grids whose top follows a height
function), so that every run gives the same GLB; every face is triangulated before the export (polish_k_pod.triangulate).
Painted shapes the 4x upscales draw smoothly (the hangar's numbers) are thin decals over the surfaces, their outlines
traced once from the upscales and written into the scripts as polygons.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z 0: the ground the
object stands on). A picture's pixel edges: x = column - left, y = top - row (each script names its picture's origin).
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.geometry import tessellate_polygon

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_gyges_wall import shear_to_camera, parse  # noqa: E402,F401
from polish_coral_manta import cut  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402

TAN_T = math.tan(math.radians(20.0))
VIEW = Vector((0.0, -math.sin(math.radians(20.0)), math.cos(math.radians(20.0))))   # towards the camera (world)
SUN = Vector((-0.6, 0.6, 1.0)).normalized()                                          # the game's sun (world)


def pal(name, index, metallic=0.3, roughness=0.5, glow=0.0, glow_index=None):
    """A palette material (it follows the level's palette); glow: emission strength in the colour of glow_index (or its
    own index)."""
    if glow > 0:
        colour = k.level_palette()[glow_index if glow_index is not None else index]
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=colour,
                          emission_strength=glow)
    return k.material(name, palette=index, metallic=metallic, roughness=roughness)


def pixels(text):
    """A picture written as two hex digits a pixel ('..' none), rows top to bottom: an int array, -1 none."""
    return np.array([[-1 if v is None else v for v in row] for row in parse(text)])


def link(name, verts, faces, mat=None, smooth=False):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    mesh.validate()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    mesh.polygons.foreach_set("use_smooth", [smooth] * len(mesh.polygons))
    mesh.update()
    return obj


# --- Solids ------------------------------------------------------------------------------------------------------------

def grid_solid(name, top, bottom_z, mat=None):
    """A closed solid from a grid of top points top[j][i] = (x, y, z) (rows j, columns i, a quad between neighbours):
    walls round its border straight down to bottom_z and a bottom face. The top's quads are split along their flatter
    diagonal (the same split every run)."""
    rows, cols = len(top), len(top[0])
    verts = [tuple(p) for row in top for p in row]
    faces = []

    def v(i, j):
        return j * cols + i
    for j in range(rows - 1):
        for i in range(cols - 1):
            a, b, c, d = v(i, j), v(i + 1, j), v(i + 1, j + 1), v(i, j + 1)
            za, zb, zc, zd = top[j][i][2], top[j][i + 1][2], top[j + 1][i + 1][2], top[j + 1][i][2]
            if abs(za - zc) <= abs(zb - zd):
                faces += [(a, b, c), (a, c, d)]
            else:
                faces += [(a, b, d), (b, c, d)]
    border = [v(i, 0) for i in range(cols)] + [v(cols - 1, j) for j in range(1, rows)] + \
        [v(i, rows - 1) for i in range(cols - 2, -1, -1)] + [v(0, j) for j in range(rows - 2, 0, -1)]
    base = len(verts)
    for idx in border:
        x, y, _ = verts[idx]
        verts.append((x, y, bottom_z))
    n = len(border)
    for q in range(n):
        a, b = border[q], border[(q + 1) % n]
        faces.append((a, base + q, base + (q + 1) % n, b))
    faces.append(tuple(base + q for q in range(n - 1, -1, -1)))
    obj = link(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def section_loft(name, sections, mat=None, closed=True):
    """A solid lofted through sections of equal point counts (lists of (x, y, z), each a closed polygon), its two ends
    closed by n-gons (closed)."""
    n = len(sections[0])
    verts = [tuple(p) for s in sections for p in s]
    faces = []
    for i in range(len(sections) - 1):
        for q in range(n):
            a, b = i * n + q, i * n + (q + 1) % n
            faces.append((a, b, b + n, a + n))
    if closed:
        faces.append(tuple(range(n - 1, -1, -1)))
        last = (len(sections) - 1) * n
        faces.append(tuple(last + q for q in range(n)))
    obj = link(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def beam(name, a, b, profile, up=(0.0, 0.0, 1.0), mat=None, cap=True):
    """A straight bar from a to b (3D), its section the polygon profile [(across, up), ...] (counter-clockwise) in the
    plane across the bar, 'up' the direction its section's second coordinate points."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    u = Vector(up)
    u = (u - d * u.dot(d)).normalized()
    s = d.cross(u).normalized()
    ring_a = [a + s * p + u * q for p, q in profile]
    ring_b = [b + s * p + u * q for p, q in profile]
    return section_loft(name, [ring_a, ring_b], mat, closed=cap)


def rect_profile(w, h, chamfer=0.0, below=0.0):
    """A bar's section: w wide, from -below to h high, its top corners chamfered."""
    c = min(chamfer, w / 2 - 1e-3, h / 2)
    if c <= 0:
        return [(-w / 2, -below), (w / 2, -below), (w / 2, h), (-w / 2, h)]
    return [(-w / 2, -below), (w / 2, -below), (w / 2, h - c), (w / 2 - c, h), (-w / 2 + c, h), (-w / 2, h - c)]


def round_profile(r, segments=8, squash=1.0, below=0.3):
    """A half-round section of radius r (its height squashed), standing on a flat foot reaching below * r under its
    axis (counter-clockwise)."""
    arc = [(r * math.cos(math.pi * i / segments), r * squash * math.sin(math.pi * i / segments))
           for i in range(segments + 1)]
    return [(r, -below * r)] + arc + [(-r, -below * r)]


def disc_profile(r, segments=12, squash=1.0):
    """A whole round (or oval) section of radius r (counter-clockwise)."""
    return [(r * math.cos(2 * math.pi * i / segments), r * squash * math.sin(2 * math.pi * i / segments))
            for i in range(segments)]


def lathe_axis(name, profile, origin, axis, around=24, squash=1.0):
    """A turned part: profile [(t, radius), ...] along axis from origin (t increasing), its ends closed by fans to the
    axis; its sections squashed towards +z (squash)."""
    o, a = Vector(origin), Vector(axis).normalized()
    side = a.cross(Vector((0.0, 0.0, 1.0)))
    if side.length < 1e-6:
        side = Vector((1.0, 0.0, 0.0))
    side.normalize()
    u = side.cross(a).normalized()
    rings = [[o + a * t + side * (r * math.cos(2 * math.pi * j / around)) +
              u * (r * squash * math.sin(2 * math.pi * j / around)) for j in range(around)] for t, r in profile]
    t0, t1 = profile[0][0], profile[-1][0]
    obj = k.loft(name, rings, None, start_point=o + a * (t0 - 0.01), end_point=o + a * (t1 + 0.01))
    k.smooth(obj, 50)
    return obj


def prism_on(name, outline, surface, z0, z1, mat=None):
    """A plan (x, y) outline raised over a surface: its bottom at surface(x, y) + z0, its top at surface(x, y) + z1 (each
    vertex on its own; flat surfaces keep flat faces)."""
    n = len(outline)
    verts = [(x, y, surface(x, y) + z0) for x, y in outline] + [(x, y, surface(x, y) + z1) for x, y in outline]
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    obj = link(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def polygon_area(loop):
    a = 0.0
    for i in range(len(loop)):
        x0, y0 = loop[i]
        x1, y1 = loop[(i + 1) % len(loop)]
        a += x0 * y1 - x1 * y0
    return a / 2


def point_in(loop, x, y):
    hit = False
    j = len(loop) - 1
    for i in range(len(loop)):
        (ax, ay), (bx, by) = loop[i], loop[j]
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
            hit = not hit
        j = i
    return hit


def decal(name, loops, surface, lift, mat):
    """A painted shape lying on a surface: loops [(x, y), ...] (outlines and the holes inside them, in any order and
    winding), filled (scanfill: a loop inside another is a hole), its points at surface(x, y) + lift; an open mesh (its
    top only)."""
    groups = []
    for lp in sorted(loops, key=lambda l: -abs(polygon_area(l))):
        owner = next((g for g in groups if point_in(g[0], *lp[0])), None)
        if owner is not None:
            owner.append(lp)
        else:
            groups.append([lp])
    verts, faces = [], []
    for g in groups:
        base = len(verts)
        flat = [p for lp in g for p in lp]
        tris = tessellate_polygon([[Vector((x, y, 0.0)) for x, y in lp] for lp in g])
        verts += [(x, y, surface(x, y) + lift) for x, y in flat]
        for t in tris:
            a, b, c = (base + i for i in t)
            pa, pb, pc = (Vector(verts[i][:2]) for i in (a, b, c))
            if (pb - pa).cross(pc - pa) < 0:   # facing up
                b, c = c, b
            faces.append((a, b, c))
    return link(name, verts, faces, mat)


def clip(obj, box):
    """The part of an open mesh (a decal) inside box (x0, x1, y0, y1), without caps; None if nothing is left."""
    x0, x1, y0, y1 = box
    out = obj.copy()
    out.data = obj.data.copy()
    bpy.context.scene.collection.objects.link(out)
    bm = bmesh.new()
    bm.from_mesh(out.data)
    for co, no in (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0))):
        if not bm.faces:
            break
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co, plane_no=no,
                               clear_outer=True)
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(out)
        return None
    bm.to_mesh(out.data)
    bm.free()
    return out


def piece(parts, box, cap_mat, decals=()):
    """A piece of a whole: each solid part's share of box (capped with cap_mat), each decal's share (clipped)."""
    bpy.context.view_layer.update()
    out = [p for p in (cut(src, box, cap_mat) for src in parts) if p is not None]
    out += [p for p in (clip(src, box) for src in decals) if p is not None]
    return out


# --- Painting ----------------------------------------------------------------------------------------------------------

def world_normal(n):
    """A face normal of the picture's plane as it points after the shear to the camera."""
    w = Vector((n.x, n.y, n.z + TAN_T * n.y))
    return w.normalized() if w.length > 1e-9 else w


def sunlit(n):
    """How much the game's sun lights a face of the picture's plane (0-1)."""
    return max(0.0, world_normal(n).dot(SUN))


# --- Pieces and output -------------------------------------------------------------------------------------------------

def unshear(objects):
    """The inverse of shear_to_camera: parts built where the world has them (a lid swung on its hinge) moved into the
    picture's plane, so that the shear puts them back."""
    for obj in objects:
        mesh = obj.data
        normals = [Vector(cn.vector) for cn in mesh.corner_normals]
        for v in mesh.vertices:
            v.co.y += v.co.z * TAN_T
        mesh.normals_split_custom_set([tuple(Vector((n.x, n.y, n.z - TAN_T * n.y)).normalized()) for n in normals])
        mesh.update()


def view_coverage(objects, w, h, centre, ground=True):
    """Which pixels of a w x h picture round centre the objects cover as the game camera sees them (built where the
    world has them: the coverage of their copies moved into the picture's plane); on the ground, what lies under it is
    hidden by it."""
    copies = copy_all(objects, "_view")
    for c in copies if ground else []:
        for v in c.data.vertices:
            v.co.z = max(v.co.z, 0.0)
    unshear(copies)
    bpy.context.view_layer.update()
    covered = mk.coverage(copies, w, h, centre=centre)
    remove(copies)
    return covered


def finish(name, parts, centre, out, options, mask=None, size=(24, 28), label=None, world=False, ground=True):
    """Checks a piece's outline as the camera sees it against its sprite's own pixels (mask: rows of bools), shears it to
    the camera (unless it is built where the world has it: world), moves its sprite's middle (centre, in the plane) to
    the origin, triangulates and joins it, exports it; returns (piece, overlap)."""
    bpy.context.view_layer.update()
    score = None
    if mask is not None:
        h, w = len(mask), len(mask[0])
        covered = view_coverage(parts, w, h, centre, ground) if world else mk.coverage(parts, w, h, centre=centre)
        score = mk.compare(label or name, covered, mask)
    if not world:
        shear_to_camera(parts)
    mk.transform(parts, Matrix.Translation((-centre[0], -centre[1], 0.0)))
    bpy.context.view_layer.update()
    triangulate(parts)
    obj = join(parts, name) if len(parts) > 1 else parts[0]
    obj.name = name
    obj.data.name = name
    drop_unused([obj])
    bpy.context.view_layer.update()
    bpy.context.scene.view_settings.view_transform = "Standard"
    mk.report(name, [obj], os.path.join(out, name + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + name, [obj], size=size)
    return obj, score


def copy_all(objects, suffix):
    """Copies of objects (their meshes too), linked to the scene."""
    out = []
    for o in objects:
        c = o.copy()
        c.data = o.data.copy()
        c.name = o.name + suffix
        bpy.context.scene.collection.objects.link(c)
        out.append(c)
    return out


def remove(objects):
    for o in objects:
        data = o.data
        bpy.data.objects.remove(o)
        if data is not None and data.users == 0:
            bpy.data.meshes.remove(data)


def hide(objects, hidden=True):
    for o in objects:
        o.hide_render = hidden


def sheet_mask(sheets, sheet, sprites, layout_w=1, large=True):
    """The pixels of sprites laid out in rows (a list of rows of sprite numbers, 0 none) of a sheet in the extracted sheets
    directory: rows of bools."""
    w, h = (24, 28) if large else (12, 14)
    rows = []
    for row in sprites:
        parts = [k.sprite_mask(os.path.join(sheets, "enemy_%s.png" % sheet), s, large) if s else
                 [[False] * w for _ in range(h)] for s in row]
        for y in range(h):
            rows.append(sum((p[y] for p in parts), []))
    return rows
