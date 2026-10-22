"""Helpers for the batch W models of wave 3 (sheet P: the asteroid levels ASTEROID1, ASTEROID2, ASTEROID?,
ASTCITY, AST. CITY and AST ROCK; wave3_w.py, the small blocks with lids; wave3_w_launcher.py, the tan launcher;
their wrecks in wave3_ao_works.py). (The block house and the works built on it, the drilling rig, the bronze pump
and the cargo pod: polish_block_house.py, polish_asteroid_rig.py, polish_bronze_pump.py, polish_cargo_pod.py.)
The sprites' pixels are in wave3_w_art.py; the parts and the build loop come from the earlier batches' kits
(wave3_s_kit: pixel frames, bevelled slabs and prisms, painting by the sprite; wave3_n_kit: whole objects cut into
their sprites' pieces, the silhouette check; wave3_p_kit: heightfield beds, chamfered plates; wave3_j_kit: palette
materials, turned parts, tubes).

The sheet's ground objects all stand on the asteroid levels' floor, which their sprites draw round them, with the
object's shadow drawn on it below and to the right: the floor is the map's and the game casts its own shadows, so
the models leave both out.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
"""
import math
import os
import sys

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
import wave3_s_kit as s  # noqa: E402,F401
import wave3_w_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, grid, paint_faces, lathe_axis, hoop, tube, catmull, sphere, rounded_box, block,  # noqa: E402,F401
                         meshes, bake)
from wave3_s_kit import Frame, Painter, slab, prism_x, prism_y, paint_sprite, pixelate, merge_flat  # noqa: E402,F401

model = n.model
pieced = n.pieced
run = n.run
merge = n.merge_by_material


# --- Outlines --------------------------------------------------------------------------------------

def rrect(x0, x1, y0, y1, radii=(0.0, 0.0, 0.0, 0.0), steps=5):
    """A rectangle with rounded corners, counter-clockwise: radii (bottom-left, bottom-right, top-right,
    top-left)."""
    bl, br, tr, tl = radii
    out = []
    for (cx, cy, r, a0) in ((x0 + bl, y0 + bl, bl, 180), (x1 - br, y0 + br, br, 270),
                            (x1 - tr, y1 - tr, tr, 0), (x0 + tl, y1 - tl, tl, 90)):
        if r <= 1e-6:
            out.append((cx, cy))
            continue
        for i in range(steps + 1):
            a = math.radians(a0 + 90 * i / steps)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def greys(prefix, metallic=0.35, roughness=0.5):
    """The grey ramp's shades 1-14 as palette materials."""
    return {v: pal(f"{prefix}_grey{v:x}", v, metallic=metallic, roughness=roughness) for v in range(1, 15)}


# --- The block house -------------------------------------------------------------------------------

def house_mats(prefix):
    g = greys(prefix, metallic=0.3, roughness=0.55)
    return {"roof": g[9], "lit": g[0xb], "shade": g[7], "seam": g[5], "wall": g[7], "gap": g[3], "bolt": g[0xc],
            "grey": g}


def paint_plate(obj, m, top=None):
    """A panel's faces: its top in `top` (the roof's grey), its chamfers lit towards the upper left and
    shaded towards the lower right, its sides as the walls."""
    top = top or m["roof"]

    def pick(c, nrm):
        if nrm.z > 0.95:
            return top
        if nrm.z < -0.5:
            return m["wall"]
        if nrm.z > 0.3:
            return m["lit"] if (nrm.x < -0.25 or nrm.y > 0.25) else m["shade"]
        return m["wall"]
    return paint_faces(obj, pick)


# --- Pieces ----------------------------------------------------------------------------------------

def rotate_about(objects, axis, angle, pivot):
    """Turns objects by angle (radians) about an axis ('X', 'Y', 'Z') through pivot."""
    m = Matrix.Translation(pivot) @ Matrix.Rotation(angle, 4, axis) @ Matrix.Translation(-Vector(pivot))
    for obj in objects:
        sh.apply_modifiers(obj)
        obj.data.transform(m)
    return objects


def cut_hole(obj, x0, x1, y0, y1, z0, z1):
    """Cuts a box out of a part (a boolean difference): wells, slots, openings."""
    sh.apply_modifiers(obj)
    cutter = k.box(obj.name + "_cutter", ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0),
                   obj.data.materials[0] if obj.data.materials else None)
    mod = obj.modifiers.new("hole", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter
    sh.apply_modifiers(obj)
    bpy.data.objects.remove(cutter)
    return obj
