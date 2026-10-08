"""Helpers for batch AR of wave 3: the animation pass. models.cfg's frame lines (frame <sheet> <sprite> <model>) let
an enemy show another model while it shows one of its animation frames; this batch makes those models for the
frames that change an object's shape (a claw unfolding, a sawblade turning, a flap swinging on its hinge, a maw
opening, a jaw dropping, a fan turning, a hatch opening). Each is built by the object's own script (imported as it
is, quiet_import: its output stays unchanged) or, for objects no earlier batch modelled (sheet #), by this batch's
own builders, posed as the frame draws it and cut into the same pieces as the first frame, so that it swaps in place.

The scripts: wave3_ar_saw.py (sheet #: the spinning claw and the dark sawblade, first frames and all their frames),
wave3_ar_flap.py (sheet A: the fire flaps swinging), wave3_ar_gyges.py (sheet N: GYGES' maw opening, its pincers),
wave3_ar_beasts.py (sheet 0: the GRYPHON's jaw; sheet I: SAVARA's airship fan; sheet 3: the hatch bunker).

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


def run():
    """Builds what the script registered (wave3_n_kit's loop for whole objects cut into pieces, wave3_j_kit's for
    single models)."""
    ao.run()


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


def quad_pieces(prefix, stem, tl, centre=(0.0, 0.0), columns=19):
    """The four pieces of an object drawn as two by two 2x2 sprites meeting at `centre` (in the whole's
    coordinates): top left sprite tl, then tl + 2, tl + 2 rows, tl + 2 rows + 2. Pieces are named prefix + sprite."""
    e = 0.01
    cx, cy = centre
    out = []
    for dx, dy, s in ((-1, 1, tl), (1, 1, tl + 2), (-1, -1, tl + 2 * columns), (1, -1, tl + 2 * columns + 2)):
        x0 = cx if dx > 0 else cx - 24
        y0 = cy if dy > 0 else cy - 28
        out.append((f"{prefix}{s}", (x0 + e, x0 + 24 - e, y0 + e, y0 + 28 - e), (x0 + 12, y0 + 14),
                    lambda s=s: sheet_mask(stem, s)))
    return out


# --- Moving parts ------------------------------------------------------------------------------------------------

def about(pivot, matrix):
    """matrix applied about the point pivot (x, y[, z])."""
    p = Vector((pivot[0], pivot[1], pivot[2] if len(pivot) > 2 else 0.0))
    return Matrix.Translation(p) @ matrix @ Matrix.Translation(-p)


def turn_z(objects, degrees, pivot):
    """Turns objects about a vertical axis through pivot (degrees counter-clockwise seen from above)."""
    return w.transform(objects, about(pivot, Matrix.Rotation(math.radians(degrees), 4, "Z")))


def swing(objects, degrees, axis_point, axis):
    """Turns objects by degrees about the line through axis_point along axis (right-handed)."""
    return w.transform(objects, about(axis_point, Matrix.Rotation(math.radians(degrees), 4, Vector(axis))))


def scale_about(objects, s, pivot):
    return w.transform(objects, about(pivot, Matrix.Scale(s, 4)))


def catmull(points, step=0.5):
    """A smooth path through tuples (x, y, z, more values...), sampled about every `step` along x, y, z."""
    pts = [tuple(p) for p in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        length = math.dist(p1[:3], p2[:3])
        count = max(1, int(math.ceil(length / step)))
        for j in range(count):
            t = j / count
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[q] + (-p0[q] + p2[q]) * t +
                                    (2 * p0[q] - 5 * p1[q] + 4 * p2[q] - p3[q]) * t2 +
                                    (-p0[q] + 3 * p1[q] - 3 * p2[q] + p3[q]) * t3) for q in range(len(p1))))
    out.append(pts[-1])
    return out


def blade(name, path, mat, squash=0.55, segments=10, step=0.5, smooth_angle=50):
    """A flat blade (or rod) along a path of (x, y, z, half width): a tube whose sections are flattened to
    `squash` of their width, lying flat (its width horizontal)."""
    pts = catmull(path, step)
    return tube(name, [p[:3] for p in pts], [max(0.12, p[3]) for p in pts], mat, segments, smooth_angle, squash)


def banded(obj, bands):
    """Paints faces by how much they look up: bands [(min normal z, material), ...] from the highest."""
    def pick(c, nrm):
        for lo, m in bands:
            if nrm.z >= lo:
                return m
        return bands[-1][1]
    return paint_faces(obj, pick)
