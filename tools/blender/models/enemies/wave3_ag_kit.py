"""Helpers for the batch AG models of wave 3 (sheet u: DELI, New Deli, BONUS and HARVEST; the glass
globe is polish_glass_globe.py's; wave3_ag_tower.py, DELI's two towers and their damaged looks): the sprites' pixels
(wave3_ag_art.py), and the frames, painting, parts and build loop of batches AA and AE (wave3_aa_kit: pixel
frames, reliefs inflated from pixel regions, painting faces by the sprite's pixel under them, stand-alone models
and whole objects cut into their sprites' pieces, the silhouette check; wave3_ae_kit: plates, pipes with
rounded bends, discs, displacements), with a few helpers of their own: relief by the sprite's brightness,
ribbed hoops, broken (jagged) ends.

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
from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_v_kit as v  # noqa: E402,F401
import wave3_aa_kit as aa  # noqa: E402,F401
import wave3_ae_kit as ae  # noqa: E402,F401
import wave3_y_kit as yk  # noqa: E402,F401
import wave3_ag_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, paint_faces, lathe_axis, hoop, tube, catmull, sphere, rounded_box, block,  # noqa: E402,F401
                         meshes, bake, sampler, transform, triangles)
from wave3_v_kit import (Frame, Painter, paint_sprite, pixelate, merge_flat, relief, outlines_of,  # noqa: E402,F401
                         lift, smoothstep)
from wave3_ae_kit import (displace_z, bumps, plate, limb, pipe, disc, superellipse, delete_faces, join,  # noqa: E402,F401
                          bisect_mesh, band_y, fillet_path, surface_z)

model = n.model
pieced = n.pieced
run = v.run
PROTECT = v.PROTECT
piece = aa.piece
grid_pieces = aa.grid_pieces
lens = aa.lens
cone = aa.cone
ellipsoid_point = aa.ellipsoid_point
loft_path = ae.loft_path
heightfield = yk.heightfield
polys_of = yk.polys_of


def frame(name, width, origin):
    """A Frame of one of wave3_ag_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


def luminance(index):
    r, g, b = k.level_palette()[index]
    return (0.3 * r + 0.59 * g + 0.11 * b) / 255.0


def brightness(f, blur=1, keep=lambda val: True):
    """A function (x, y) -> the sprite's brightness (0-1) there, smoothed."""
    return sampler(f.g, (f.ox, f.oy), value=luminance, blur=blur, keep=lambda val: val is not None and keep(val))


def emboss(obj, field, amount, centre=None, min_nz=0.15):
    """Moves the vertices of faces looking up (normal z over min_nz) out along their direction from
    `centre` (default: their normals) by amount * field(x, y), faded towards the silhouette: relief
    following the sprite (bright raised, dark sunk)."""
    sh.apply_modifiers(obj)
    obj.data.update()
    moves = []
    for vt in obj.data.vertices:
        nrm = (vt.co - Vector(centre)).normalized() if centre is not None else vt.normal
        if nrm.z <= min_nz:
            moves.append(None)
            continue
        fade = smoothstep(min_nz, min_nz + 0.35, nrm.z)
        moves.append(nrm * amount * field(vt.co.x, vt.co.y) * fade)
    for vt, mv in zip(obj.data.vertices, moves):
        if mv is not None:
            vt.co += mv
    obj.data.update()
    return obj


def ribbed_hoop(name, centre, radius, minor, mat, axis="Y", segments=32, sides=8, squash=1.0):
    """A ring (rib) round an axis along X or Y through centre: a frame rib of an open hull."""
    obj = ae.torus(name, (0.0, 0.0, 0.0), radius, minor, mat, segments, sides)
    rot = Matrix.Rotation(math.radians(90), 4, "X") if axis == "Y" else Matrix.Rotation(math.radians(90), 4, "Y")
    obj.data.transform(Matrix.Translation(Vector(centre)) @ Matrix.Scale(squash, 4, (0, 0, 1)) @ rot)
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def jag(obj, axis_point, direction, depth, scale=0.9, seed=0.0):
    """Breaks a part's end: the vertices within `depth` of its end along `direction` (a unit vector, the end
    at axis_point) pulled back by noise, so the end looks snapped off rather than cut."""
    sh.apply_modifiers(obj)
    d = Vector(direction).normalized()
    p0 = Vector(axis_point)
    off = Vector((seed * 5.3, seed * 2.9, seed * 7.1))
    for vt in obj.data.vertices:
        t = (vt.co - p0).dot(d)
        if t > -depth:
            pull = (0.5 + 0.5 * noise.noise(vt.co / scale + off)) * depth
            vt.co -= d * pull * smoothstep(-depth, 0.0, t)
    obj.data.update()
    return obj


def scorch(obj, centre, radius, dark_mat, chance=0.6, seed=1.0):
    """Paints the faces within `radius` of centre (x, y) dark (soot), patchily by noise."""
    cx, cy = centre
    off = Vector((seed * 3.1, seed * 1.7, seed * 2.3))

    def pick(c, nrm):
        d = math.hypot(c.x - cx, c.y - cy) / radius
        if d > 1.0:
            return None
        if 0.5 + 0.5 * noise.noise(Vector((c.x, c.y, c.z)) / 1.6 + off) < chance * (1.0 - d * d) + 0.15:
            return dark_mat
        return None
    return paint_faces(obj, pick)


def ico_ellipsoid(name, centre, radii, mat, subdivisions=4, smooth_angle=70):
    """An ellipsoid of even triangles (an icosphere scaled to radii): faces of about one size all over, for
    painting by the sprite's pixels without the crowding of a UV sphere's poles."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    obj.data.name = name
    obj.data.transform(Matrix.Translation(Vector(centre)) @ Matrix.Diagonal((*radii, 1.0)))
    if mat is not None:
        obj.data.materials.append(mat)
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)
