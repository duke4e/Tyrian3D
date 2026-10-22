"""Helpers for batch AR of wave 3: the animation pass. models.cfg's frame lines (frame <sheet> <sprite> <model>) let
an enemy show another model while it shows one of its animation frames; this batch makes those models for the
frames that change an object's shape (a flap swinging on its hinge, a maw opening, a jaw dropping, a fan turning, a
hatch opening). Each is built by the object's own script (imported as it is, quiet_import: its output stays
unchanged), posed as the frame draws it and cut into the same pieces as the first frame, so that it swaps in place.

The scripts (the spinning claw and the dark sawblade of sheet # are polish_spin_claw.py's, GYGES' maw opening and
its pincers polish_gyges_maw.py's):
wave3_ar_beasts.py (sheet 0: the GRYPHON's jaw).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera); the origin
is the whole object's centre (for objects the game draws in pieces) or the sprite's centre.
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
import wave3_ao_kit as ao  # noqa: E402,F401
from wave3_j_kit import (pal, paint_faces, tube, sphere, meshes, bake, triangles, lathe_axis, column,  # noqa: E402,F401
                         hoop)

quiet_import = ao.quiet_import
forget = ao.forget
pieced = n.pieced
ENEMIES = w.ENEMIES


# --- Sprites of the extracted sheets (for --check) ---------------------------------------------------------------

def sheets_dir():
    """The directory of the sheets TYR3D_EXTRACT wrote (--check <dir>), or None."""
    d = k.args().get("check")
    return d if d and os.path.isdir(d) else None


def sheet_mask(stem, sprite, large=True):
    """The coverage of a sprite of an extracted sheet (rows of bools), or all False without --check <dir>."""
    from sprite_profile import sprite_pixels
    d = sheets_dir()
    w_, h_ = (24, 28) if large else (12, 14)
    if d is None:
        return [[False] * w_ for _ in range(h_)]
    return [[p is not None for p in row] for row in sprite_pixels(os.path.join(d, stem + ".png"), sprite, large)]


# --- Moving parts ------------------------------------------------------------------------------------------------

def about(pivot, matrix):
    """matrix applied about the point pivot (x, y[, z])."""
    p = Vector((pivot[0], pivot[1], pivot[2] if len(pivot) > 2 else 0.0))
    return Matrix.Translation(p) @ matrix @ Matrix.Translation(-p)


def swing(objects, degrees, axis_point, axis):
    """Turns objects by degrees about the line through axis_point along axis (right-handed)."""
    return w.transform(objects, about(axis_point, Matrix.Rotation(math.radians(degrees), 4, Vector(axis))))
