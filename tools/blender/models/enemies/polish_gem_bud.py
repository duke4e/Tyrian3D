"""GEM WAR's gem bud (sheet V 38 green; also V 19 blue and V 57 red: 1x1, 12 x 14 pixels), polished
(2026-10-18; it replaces wave2_g.py's low-poly gem).

A cut gem, a rhombus from above (its corners up, down and to the sides, as the sprite draws it),
held up on a short stem like a flower bud: the stem rises from the ground below the gem's lower
corner (the sprite's stub at rows 12-13) and curves in under it to the culet, where four small
sepals cup the gem. The gem has a small bright table, a crown in two tiers of facets with a narrow
bright facet along each of the four ridges that run from the table to the corners (the sprite's
light cross), a dark bezel and girdle round its edge (the sprite's dark outline) and a deeper
pavilion under it.

All its materials are palette shades of the green ramp (2): the game gives the model each sprite's
ramp (models.cfg: color=sprite; V 19 blue 3, V 38 green 2, V 57 red 4), keeping the shades (index
& 15): table 15, ridges 14, crown 13 and 10, pavilion 10 (its ridges 12), bezel and girdle 8, stem
8, sepals 9. No emission: its colour would not follow the sprite's.

usage: Blender -b --python polish_gem_bud.py -- [--out <file.glb>] [--preview <prefix>]
       [--sheets <TYR3D_EXTRACT sheets directory>]   (--sheets: print the silhouette overlap)
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402

CX, CY = 0.0, -0.5   # the gem's middle (between the sprite's columns 5 and 6, on row 7)
RIDGE = 0.085        # each ridge's narrow facet, as a fraction of the gem's edge on each side

# The gem from the culet (a point) up: its cross-sections (height z, half-diagonal a) and the bands
# of facets between them; the last cross-section is the table's edge.
CULET_Z = 1.7
RINGS = [(2.9, 3.4), (4.1, 5.25), (4.65, 5.25), (4.95, 4.25), (5.9, 3.15), (7.15, 1.45)]
BANDS = ["pavilion", "girdle", "girdle", "crown_low", "crown_high"]
PAVILION_SLOPE = math.atan2(RINGS[0][0] - CULET_Z, RINGS[0][1] / math.sqrt(2))  # the lower pavilion's


def rhombus(a, z):
    """A cross-section of the gem: its corners east, north, west and south at half-diagonal a, each
    cut by a ridge's narrow facet: 8 points, counter-clockwise from above, the two of each corner
    in a row (east first)."""
    corners = [Vector((a, 0)), Vector((0, a)), Vector((-a, 0)), Vector((0, -a))]
    t = RIDGE * a * math.sqrt(2)
    out = []
    for i, c in enumerate(corners):
        prev, nxt = corners[i - 1], corners[(i + 1) % 4]
        for p in (c + (prev - c).normalized() * t, c + (nxt - c).normalized() * t):
            out.append(Vector((CX + p.x, CY + p.y, z)))
    return out


def gem(mats):
    """The gem: one flat-faceted mesh. mats: {material name: material}."""
    rings = [rhombus(a, z) for z, a in RINGS]
    n = 8
    vertices = [v for r in rings for v in r]
    culet = len(vertices)
    vertices.append(Vector((CX, CY, CULET_Z)))
    faces, face_mats = [], []

    def idx(r, s):
        return r * n + s % n

    def mat(band, s):
        ridge = s % 2 == 0  # even sectors join a corner's two points: a ridge's narrow facet
        if band == "girdle":
            return "girdle"
        if band.startswith("crown"):
            return "ridge" if ridge else band
        return "pavilion_ridge" if ridge else "pavilion"

    for s in range(n):  # the culet up to the first ring
        faces.append((culet, idx(0, s + 1), idx(0, s)))
        face_mats.append(mat("pavilion", s))
    for r in range(len(rings) - 1):
        for s in range(n):
            faces.append((idx(r, s), idx(r, s + 1), idx(r + 1, s + 1), idx(r + 1, s)))
            face_mats.append(mat(BANDS[r], s))
    faces.append(tuple(idx(len(rings) - 1, s) for s in range(n)))  # the table
    face_mats.append("table")
    obj = k.mesh_object("gem", vertices, faces)
    for name in mats:
        obj.data.materials.append(mats[name])
    names = list(mats)
    for poly, name in zip(obj.data.polygons, face_mats):
        poly.material_index = names.index(name)
        poly.use_smooth = False
    k.recalc_normals(obj)
    return obj


def tube(name, points, radii, mat, segments=12):
    """A round stem through points (x, y, z), its radius per point; the ends closed."""
    pts = [Vector(p) for p in points]
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        tangent = (b - a).normalized()
        side = tangent.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        up = side.cross(tangent).normalized()
        rings.append([p + (side * math.cos(2 * math.pi * j / segments) + up * math.sin(2 * math.pi * j / segments))
                      * radii[i] for j in range(segments)])
    obj = k.loft(name, rings, mat)
    return k.smooth(obj, 60)


def sepal(name, phi, mat, length=3.0):
    """A pointed sepal lying on the lower pavilion's facet in direction phi (from above), from the
    culet up, its tip curling a little away from the gem."""
    u = Vector((math.cos(phi), math.sin(phi), 0))
    a = PAVILION_SLOPE
    along = Vector((u.x * math.cos(a), u.y * math.cos(a), math.sin(a)))  # up the facet
    out = Vector((u.x * math.sin(a), u.y * math.sin(a), -math.cos(a)))  # away from the gem
    across = along.cross(out)
    rings = []
    for t, half_width in ((0.0, 0.3), (0.2, 0.75), (0.5, 0.8), (0.8, 0.45), (0.97, 0.08)):
        rings.append(k.ring(t * length, half_width, 0.22 * half_width / 0.8 + 0.06, 10, z=0.05 + 0.45 * t * t))
    leaf = k.loft(name, rings, mat, end_point=(0, length * 1.02, 0.05 + 0.45))
    basis = Matrix(((across.x, along.x, out.x, CX), (across.y, along.y, out.y, CY),
                    (across.z, along.z, out.z, CULET_Z), (0, 0, 0, 1)))
    leaf.data.transform(basis)
    k.recalc_normals(leaf)
    return k.smooth(leaf, 60)


def cut_below(obj, z=0.0):
    """Cuts the part of obj below z away and closes the cut (it stands on the ground)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    result = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=(0, 0, z), plane_no=(0, 0, -1),
                                    clear_outer=True)
    edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid and
             len(e.link_faces) == 1]
    if edges:
        bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bm.to_mesh(obj.data)
    bm.free()
    k.recalc_normals(obj)


def build():
    k.reset()
    mats = {
        "table": k.material("gembud_table", palette=0x2f, metallic=0.1, roughness=0.08),
        "ridge": k.material("gembud_ridge", palette=0x2e, metallic=0.1, roughness=0.08),
        "crown_high": k.material("gembud_crown_high", palette=0x2d, metallic=0.1, roughness=0.1),
        "crown_low": k.material("gembud_crown_low", palette=0x2a, metallic=0.1, roughness=0.1),
        "girdle": k.material("gembud_girdle", palette=0x28, metallic=0.1, roughness=0.45),
        "pavilion": k.material("gembud_pavilion", palette=0x2a, metallic=0.1, roughness=0.12),
        "pavilion_ridge": k.material("gembud_pavilion_ridge", palette=0x2c, metallic=0.1, roughness=0.1),
    }
    gem(mats)
    stem_mat = k.material("gembud_stem", palette=0x28, metallic=0.05, roughness=0.45)
    sepal_mat = k.material("gembud_sepal", palette=0x29, metallic=0.05, roughness=0.4)
    # The stem: from the ground below the gem's lower corner (the sprite's stub), up and in under the
    # gem to its culet.
    stem = tube("stem", [(CX, -7.0, -0.45), (CX, -6.6, 0.5), (CX, -5.8, 1.15), (CX, -4.6, 1.4), (CX, -3.0, 1.35),
                         (CX, -1.6, 1.45), (CX, CY, 1.8)],
                [1.15, 1.0, 0.95, 0.92, 0.9, 0.85, 0.7], stem_mat)
    cut_below(stem)
    # The calyx: four small sepals from the culet up the pavilion's facets, holding the gem as a bud.
    for i in range(4):
        sepal(f"sepal{i}", math.radians(45 + 90 * i), sepal_mat)

    options = k.args()
    if "sheets" in options:
        k.check_silhouette(os.path.join(options["sheets"], "enemy_V.png"), 38, large=False)
    # The game shows colours as they are (no filmic tone mapping): so do the previews.
    bpy.context.scene.view_settings.view_transform = "Standard"
    k.finish(os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies", "gem_bud.glb"), size=(12, 14))


build()
