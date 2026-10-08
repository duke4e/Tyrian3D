"""Batch AR of wave 3, sheet A (written a in models.cfg): the fire flaps of APPROACH, MISTAKES and SOH JIN swinging on
their hinges, for frame lines. The flaps (fire_flap_r_top, fire_flap_r_bottom over A 237 and 275, hinged on the left,
and their mirror images fire_flap_l_top, fire_flap_l_bottom over A 7 and 45) are wave2_h.py's: its builder
(fire_flap, imported as it is) builds the whole flap closed, lying flat with its fire face up, and swings it up about
its hinge to stand on edge, as the enemies' first frame draws it. A level event makes them flap: down and up again,
237 235 233 231 233 235 237 (and 275 273 271 269 ..., 7 5 3 1 ..., 45 43 41 39 ...). The frames are the flap swung
part of the way: models here are the same builder's flap swung up 65 degrees (235, 273 and the mirrored 5, 43),
45 degrees (233, 271, 3, 41) and lying flat (231, 269, 1, 39), measured from how far each frame's fire face reaches
out from the hinge (11 pixels flat). Same pieces, origins and options as the first frame's (yaw=0, origin).

usage: Blender -b --factory-startup -P wave3_ar_flap.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>]
"""
import math
import os
import sys

from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ar_kit as kit  # noqa: E402

h = kit.quiet_import("wave2_h")   # its build loop, run on import, builds nothing
hk = h.kit                         # wave2_h_kit


class _Swung:
    """wave2_h's Matrix while a flap is built: its one swing about the hinge (-90 degrees about Y, the flap standing
    on edge) turned into `degrees` up from lying flat; everything else as Matrix."""

    def __init__(self, degrees):
        self.degrees = degrees

    def __getattr__(self, name):
        return getattr(Matrix, name)

    def Rotation(self, angle, size, axis):
        if axis == "Y" and abs(angle - math.radians(-90)) < 1e-9:
            angle = math.radians(-self.degrees)
        return Matrix.Rotation(angle, size, axis)


def flap(piece, mirror, degrees):
    """wave2_h's fire flap (the top or bottom sprite's piece, mirrored for the left flaps), swung `degrees` up from
    lying flat (90: standing on edge, its first frame)."""
    saved = h.Matrix
    h.Matrix = _Swung(degrees)
    try:
        h.fire_flap(piece, mirror)
    finally:
        h.Matrix = saved


# (frame of the right flap's top, of its bottom, of the left flap's top, of its bottom, degrees up)
FRAMES = [(235, 273, 5, 43, 65.0), (233, 271, 3, 41, 45.0), (231, 269, 1, 39, 0.0)]

E = hk.ENEMIES
MODELS = []
for rt, rb, lt, lb, deg in FRAMES:
    for sprite, piece, mirror in ((rt, "top", False), (rb, "bottom", False), (lt, "top", True), (lb, "bottom", True)):
        MODELS.append((f"fire_flap_{sprite}", lambda piece=piece, mirror=mirror, deg=deg: flap(piece, mirror, deg),
                       [("A", sprite, True)], E))

if __name__ == "__main__":
    hk.run(MODELS)
