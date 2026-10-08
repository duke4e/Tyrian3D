"""Helpers for the batch AI models of wave 3 (sheet 0: GRYPHON's boss and BOTANY's ground creatures,
wave3_ai.py and wave3_ai_gryphon.py; the coins sheet's remaining items, items/wave3_ai_items.py): the sprites'
pixels (wave3_ai_art.py), and the frames, painting, parts and build loop of batch AE (wave3_ae_kit: pixel
frames, reliefs inflated from pixel regions, painting faces by the sprite's pixel under them, limbs, lenses,
bumpy peel, stand-alone models and whole objects cut into their sprites' pieces, the silhouette check). Its own:
the items' build loop (the same loop, exporting to assets/models/items), berries, faceted gems and letters.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
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
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_v_kit as v  # noqa: E402,F401
import wave3_ae_kit as ae  # noqa: E402,F401
import wave3_ai_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, paint_faces, lathe_axis, tube, catmull, sphere, rounded_box, meshes, bake,  # noqa: E402,F401
                         transform, triangles)
from wave3_v_kit import (Frame, Painter, paint_sprite, merge_flat, relief, outlines_of, mirror_copies,  # noqa: E402,F401
                         lift, smoothstep)
from wave3_ae_kit import (displace_z, bumps, plate, limb, band_y, pipe, disc, superellipse, delete_faces,  # noqa: E402,F401
                          join, bisect_mesh, rotate_z, lens, ellipsoid_point, torus, loft_path, piece, grid_pieces)

model = n.model
pieced = n.pieced
PROTECT = v.PROTECT
ITEMS = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "items")


def frame(name, width, origin):
    """A Frame of one of wave3_ai_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


def run(items=False):
    """The build loop of batch AE (wave3_v_kit.run); items=True exports to assets/models/items."""
    saved = n.ENEMIES
    if items:
        n.ENEMIES = ITEMS
    try:
        v.run()
    finally:
        n.ENEMIES = saved


# --- Shapes ----------------------------------------------------------------------------------------------

def ellipsoid(name, centre, radii, mat, segments=24, rings=12, angle=60):
    """An ellipsoid (wave3_j_kit.sphere)."""
    return sphere(name, tuple(centre), tuple(radii), mat, segments, rings, angle)


def turned(obj, degrees, axis="Z", pivot=(0.0, 0.0, 0.0)):
    """Turns a part's mesh about an axis through pivot."""
    p = Vector(pivot)
    obj.data.transform(Matrix.Translation(p) @ Matrix.Rotation(math.radians(degrees), 4, axis) @
                       Matrix.Translation(-p))
    return obj


def berry(name, centre, radius, mat, squash=0.9, segments=16, rings=8):
    """A round berry (a grape): an ellipsoid a little flattened towards the camera."""
    return sphere(name, tuple(centre), (radius, radius, radius * squash), mat, segments, rings, 70)


def pip(name, centre, normal, radii, mat, sink=0.1, segments=6, rings=4):
    """A small low ellipsoid (radii: across, across, thickness) set into a surface at `centre`, its flat axis
    along the surface's `normal`: seeds, rivets."""
    nrm = Vector(normal).normalized()
    obj = sphere(name, (0.0, 0.0, 0.0), tuple(radii), mat, segments, rings, 80)
    rot = nrm.to_track_quat("Z", "Y").to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(Vector(centre) - nrm * sink) @ rot)
    k.recalc_normals(obj)
    return obj


def facet_gem(name, outline, crown_z, table_scale, table_z, pavilion_z, mats):
    """A cut stone over a convex girdle outline [(x, y)] (counter-clockwise): crown facets from the girdle at
    crown_z up to a table (the outline scaled by table_scale about its centre) at table_z, a pavilion down to a
    point at pavilion_z. mats: (crown, table, pavilion)."""
    cx = sum(p[0] for p in outline) / len(outline)
    cy = sum(p[1] for p in outline) / len(outline)
    m = len(outline)
    verts = [(x, y, crown_z) for x, y in outline]
    verts += [(cx + (x - cx) * table_scale, cy + (y - cy) * table_scale, table_z) for x, y in outline]
    verts.append((cx, cy, pavilion_z))
    faces, which = [], []
    for i in range(m):
        j = (i + 1) % m
        faces.append((i, j, m + j, m + i))
        which.append(0)
        faces.append((j, i, 2 * m))
        which.append(2)
    faces.append(tuple(range(m, 2 * m)))
    which.append(1)
    obj = k.mesh_object(name, verts, faces)
    k.recalc_normals(obj)
    for mat in mats:
        obj.data.materials.append(mat)
    for poly, idx in zip(obj.data.polygons, which):
        poly.material_index = idx
    return obj


def polys_where(f, keep, smooth=1, epsilon=0.3, min_area=0.4, grow=0.0):
    """The outlines of the frame's pixels keep(index, column, row) accepts."""
    return outlines_of(f, keep, grow=grow, smooth=smooth, epsilon=epsilon, min_area=min_area)


def slab_polys(name, polys, z0, z1, mat, bevel=0.35, segments=2, angle=40):
    """Each polygon extruded from z0 to z1, its edges bevelled; joined into one part."""
    parts = []
    for i, poly in enumerate(polys):
        parts.append(v.slab(f"{name}_{i}", poly, z0, z1, mat, bevel=bevel, segments=segments, angle=angle))
    return join(parts, name)


def relief_map(name, fr, keep, height, mat, edge=1.4, bevel=1.0, emboss=1.6, fine_blur=1, coarse_blur=3, spacing=0.5,
               smooth=1, epsilon=0.3, min_area=1.0, angle=45, sigma=0.9, limit=0.35):
    """wave3_ab_kit.relief with the sprite's shading embossed from a smoothed field (fine_blur) against a more
    smoothed one (coarse_blur): its larger ridges and grooves stand out, not its single pixels."""
    import wave3_ab_kit as ab
    polys = ab.polys_of(fr, keep, smooth=smooth, epsilon=epsilon, min_area=min_area, sigma=sigma)
    fine = ab.field(fr, lambda v, c, r: ab.brightness(v), blur=fine_blur)
    coarse = ab.field(fr, lambda v, c, r: ab.brightness(v), blur=coarse_blur)

    def top(x, yy, e):
        h = height(x, yy) + emboss * max(-limit, min(limit, fine(x, yy) - coarse(x, yy))) * e
        return max(0.3, h - bevel * (1.0 - e) ** 2)
    return ab.q.heightfield(name, polys, top, mat, spacing=spacing, smooth_angle=angle, edge=edge)


def flatten_under(objects, z=0.0):
    """Cuts away what lies below z (closing the cut): parts standing on their layer."""
    return sh.flat_bottom(objects, z)
