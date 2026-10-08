"""Helpers for the batch AA models of wave 3 (sheet E: STARGATE's lava grubs, the big dark orb of FLEET,
MISTAKES and STARGATE, the tan spiked mine, BUBBLES' boiling bubbles, ASTEROIDS' crater with its glass domes,
the boulders in the pit of TYRIAN and HOLES): the sprites' pixels (wave3_aa_art.py), and the parts, painting
and build loop of batch V (wave3_v_kit: pixel frames, reliefs inflated from pixel regions, painting faces by
the sprite's pixel under them, mirroring; wave3_n_kit: stand-alone models and whole objects cut into their
sprites' pieces, the silhouette check), with a few parts of their own: pieces of any size, cones, convex
rocks, glass domes on a pedestal.

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
import wave3_p_kit as p  # noqa: E402,F401
import wave3_v_kit as v  # noqa: E402,F401
import wave3_aa_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, grid, paint_faces, lathe_axis, hoop, tube, catmull, sphere, rounded_box,  # noqa: E402,F401
                         meshes, bake, sampler, transform, lumpy)
from wave3_v_kit import (Frame, Painter, paint_sprite, pixelate, merge_flat, relief, outlines_of,  # noqa: E402,F401
                         bands_of, mirror_scene, lift, smoothstep)

model = n.model
pieced = n.pieced
run = v.run
PROTECT = v.PROTECT


# --- Pieces ----------------------------------------------------------------------------------------

def piece(name, f, c0, r0, width=24, height=28):
    """A width x height piece of a whole object at pixel (c0, r0) of frame f: (piece name, its box in the
    whole's coordinates, its sprite's centre there, its mask for --check)."""
    x0, y1 = f.left(c0) if hasattr(f, "left") else c0 - f.ox, f.oy - r0
    e = 0.01  # faces lying on a piece's edge stay with neither piece
    return (name, (x0 + e, x0 + width - e, y1 - height + e, y1 - e), (x0 + width / 2, y1 - height / 2),
            lambda: f.mask((c0, c0 + width, r0, r0 + height)))


def grid_pieces(prefix, f, names, columns, rows, width=24, height=28):
    """The pieces of a whole object laid out as `columns` x `rows` sprites from its top left pixel: names
    row by row."""
    out = []
    for j in range(rows):
        for i in range(columns):
            out.append(piece(prefix + names[j * columns + i], f, i * width, j * height, width, height))
    return out


# --- Parts -----------------------------------------------------------------------------------------

def cone(name, base, tip, radius, mat, segments=10, tip_radius=0.15, smooth_angle=50):
    """A cone from a base centre to a tip (a spike), its tip slightly rounded."""
    base, tip = Vector(base), Vector(tip)
    length = (tip - base).length
    profile = [(0.0, radius), (length * 0.55, radius * 0.55), (length * 0.92, tip_radius * 1.6), (length, tip_radius)]
    return lathe_axis(name, profile, mat, tuple(base), tuple((tip - base).normalized()), segments,
                      smooth_angle=smooth_angle)


def convex_rock(name, points, mat=None):
    """A rock as the convex hull of points (x, y, z): a few points round its foot and a few for its top
    make an angular boulder with flat facets."""
    bm = bmesh.new()
    for pt in points:
        bm.verts.new(pt)
    bmesh.ops.convex_hull(bm, input=bm.verts[:])
    # Leave out what the hull left inside, and the facets under the ground.
    for vt in [vt for vt in bm.verts if not vt.link_faces]:
        bm.verts.remove(vt)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def subdivide_faces(obj, cuts=1):
    """Splits every face (more faces to paint by the sprite), keeping the facets flat."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def dome_parts(prefix, f, painter, base_mats, centre_dome, radii_dome, centre_base, radii_base, base_height,
               dome_height, default=None):
    """A glass dome on a grey pedestal, as ASTEROIDS' red and blue domes: a bevelled ring of grey steel
    (centre_base, radii_base (x, y), base_height high, its top edge lit, a dark groove round its top)
    and on it a glossy dome (centre_dome, radii (x, y), dome_height above the ring) painted by the
    sprite's pixels (painter; `default` where the sprite has none). Returns the parts."""
    bx, by = centre_base
    rx, ry = radii_base
    light, mid, dark = base_mats
    parts = []
    # The pedestal: a short rounded drum.
    rings = []
    profile = [(0.0, 1.0, 0.0), (base_height * 0.55, 1.0, 0.0), (base_height - 0.6, 0.985, 0.0),
               (base_height - 0.15, 0.95, 0.0), (base_height, 0.9, 0.0)]
    seg = 48
    for z, scale, _ in profile:
        rings.append([Vector((bx + rx * scale * math.cos(2 * math.pi * i / seg),
                              by + ry * scale * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)])
    verts = [pt for r in rings for pt in r]
    faces = []
    for j in range(len(rings) - 1):
        for i in range(seg):
            a, b = j * seg + i, j * seg + (i + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    top_ring = (len(rings) - 1) * seg
    verts.append(Vector((bx, by, base_height)))
    faces += [(top_ring + i, top_ring + (i + 1) % seg, len(verts) - 1) for i in range(seg)]
    drum = k.mesh_object(prefix + "_pedestal", verts, faces, mid)
    k.recalc_normals(drum)
    k.smooth(drum, 35)
    paint_faces(drum, lambda c, nrm: light if (nrm.z > 0.3 and (nrm.x < 0.2 or nrm.y > 0.2)) else
                (mid if nrm.z > 0.3 else (dark if c.z < base_height * 0.5 else mid)))
    parts.append(drum)
    # A dark groove round the dome's foot.
    cx, cy = centre_dome
    dx, dy = radii_dome
    parts.append(hoop(prefix + "_groove", (cx, cy, base_height), [(dx - 0.4, -0.2), (dx + 0.7, -0.2), (dx + 0.7, 0.3),
                                                                   (dx - 0.4, 0.3)], dark, segments=48,
                      scale_y=dy / dx))
    dome = sphere(prefix + "_dome", (cx, cy, base_height - 0.2), (dx, dy, dome_height + 0.2), default, 72, 36)
    sh.cut_planes([dome], [((0, 0, base_height - 0.1), (0, 0, -1))])
    # Painted by the sprite's shades, smoothed (no pixel steps on the glass).
    paint_sprite(dome, f, painter, wall_steps=-1, default=default, blur=1, probe=-1.0)
    parts.append(dome)
    return parts


def lens(name, centre, normal, radii, mat, sink=0.2, segments=32):
    """A flattened ellipsoid (radii: across, across, thickness) set into a curved surface at `centre`, its
    flat axis along the surface's `normal` and sunk `sink` into it: eyes and lights flush with a shell."""
    nrm = Vector(normal).normalized()
    obj = sphere(name, (0.0, 0.0, 0.0), radii, mat, segments, max(8, segments // 3))
    rot = nrm.to_track_quat("Z", "Y").to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(Vector(centre) - nrm * sink) @ rot)
    k.recalc_normals(obj)
    return obj


def ellipsoid_point(centre, radii, x, y):
    """The point of an ellipsoid's top over (x, y) and the surface's normal there."""
    cx, cy, cz = centre
    rx, ry, rz = radii
    q = max(0.0, 1.0 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2)
    z = cz + rz * math.sqrt(q)
    nrm = Vector(((x - cx) / rx ** 2, (y - cy) / ry ** 2, (z - cz) / rz ** 2)).normalized()
    return Vector((x, y, z)), nrm


def paint_facets(obj, shade, material, wall_drop=1.0, under=None, samples=3):
    """Paints each face of a faceted part with one colour: material(shade) of the mean of shade(x, y) over the
    face (its centre and points towards its corners); steep faces `wall_drop` darker, faces looking down
    `under`."""
    mesh = obj.data
    names = [m.name for m in mesh.materials]
    for poly in mesh.polygons:
        if under is not None and poly.normal.z < -0.2:
            mat = under
        else:
            c = poly.center
            pts = [c] + [c + (mesh.vertices[i].co - c) * (j / samples) for i in poly.vertices for j in range(1, samples)]
            s = sum(shade(q.x, q.y) for q in pts) / len(pts)
            if poly.normal.z < 0.45:
                s -= wall_drop
            mat = material(s)
        if mat.name not in names:
            mesh.materials.append(mat)
            names.append(mat.name)
        poly.material_index = names.index(mat.name)
    return obj


def blobs(g, keep, min_size=1):
    """The 8-connected groups of a grid's pixels keep(index) accepts: (centre column, centre row, pixel
    count, the brightest index), the centre in continuous pixel coordinates (column + 0.5 is a pixel's
    middle)."""
    h, wd = len(g), len(g[0])
    seen = [[False] * wd for _ in range(h)]
    out = []
    for r in range(h):
        for c in range(wd):
            if seen[r][c] or not keep(g[r][c]):
                continue
            stack, cells = [(r, c)], []
            seen[r][c] = True
            while stack:
                rr, cc = stack.pop()
                cells.append((rr, cc))
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        r2, c2 = rr + dr, cc + dc
                        if 0 <= r2 < h and 0 <= c2 < wd and not seen[r2][c2] and keep(g[r2][c2]):
                            seen[r2][c2] = True
                            stack.append((r2, c2))
            if len(cells) < min_size:
                continue
            best = max((g[rr][cc] for rr, cc in cells), key=lambda v: v & 15)
            out.append((sum(cc for _, cc in cells) / len(cells) + 0.5, sum(rr for rr, _ in cells) / len(cells) + 0.5,
                        len(cells), best))
    return out
