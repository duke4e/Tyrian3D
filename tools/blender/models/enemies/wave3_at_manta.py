"""Batch AT of wave 3 (the second animation pass), sheet T: CORAL's manta beating its wings, for frame lines. Built by
batch V's own builder (wave3_v_sea.py's manta_whole, imported as it is, its output unchanged), posed as the frames draw
it and cut as the first frame's wing pieces are (origin, yaw=0 as those).

- coral_manta_wing_<sprite> (T 235, 165 for the left wing, enemy 1206, coral_manta_wing_left; T 239, 167 for the right
  one, enemy 1209, coral_manta_wing_right): the wings beat, 197 235 235 235 235 165 165 165 165 235 ... 197 (and 201
  239 ... 167 ...): the sprites draw them shorter and shorter as they rise, their tips 4 and 8 pixels further in. The
  whole manta is built and its wings bent up about their roots at the wing pieces' inner edges (x = -12 and 12, where
  they meet the back, which doesn't move): 38 and 52 degrees, the bend spread over 3 pixels, so that seen from above
  each reaches where the frame draws it. The back (199) and the head (237, whose frames only blow bubbles) don't
  change.

usage: Blender -b --factory-startup -P wave3_at_manta.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_at_kit as kit  # noqa: E402

vs = kit.quiet_import("wave3_v_sea")
kit.forget()

HINGE_X = 12.0        # the wings' roots: the wing pieces' inner edges
BEND = 3.0            # the bend is spread over this many pixels outboard of the root


def hinge_z():
    """The body's middle height at the roots (wave3_v_sea's droop there, plus half its relief)."""
    return 4.6 - 0.1 * abs(HINGE_X + vs.MANTA_AXIS) + 0.9


def bend_point(d, h, angle):
    """Where a point `d` outboard of the root and `h` above the root's height goes when the wing is bent up by
    `angle` (radians): (how far outboard, how high above the root), along a centre line whose angle grows evenly
    from 0 at the root to `angle` at BEND and stays so beyond."""
    if d <= 0.0:
        return d, h
    steps = max(1, int(math.ceil(d / 0.1)))
    dd = d / steps
    px = pz = 0.0
    for i in range(steps):
        s_ = (i + 0.5) * dd
        a = angle * min(1.0, s_ / BEND)
        px += math.cos(a) * dd
        pz += math.sin(a) * dd
    a = angle * min(1.0, d / BEND)
    # The normal of the bent centre line (perpendicular to it, pointing up).
    return px - math.sin(a) * h, pz + math.cos(a) * h


def manta_flap(degrees):
    """wave3_v_sea's manta with both wings bent up by `degrees` about their roots."""
    vs.manta_whole()
    kit.w.bake()
    zh = hinge_z()
    angle = math.radians(degrees)
    for obj in kit.w.meshes():
        for vt in obj.data.vertices:
            x, y, z = vt.co
            side = -1.0 if x < 0 else 1.0
            d = abs(x) - HINGE_X
            if d <= 0.0:
                continue
            u, hz = bend_point(d, z - zh, angle)
            vt.co = Vector((side * (HINGE_X + u), y, zh + hz))
        obj.data.update()


# The wing pieces' boxes and centres, as wave3_v_sea cuts coral_manta_wing_left and _right.
LEFT = ((-36.0, -12.0, -10.0, 18.0), (-24.0, 4.0))
RIGHT = ((12.0, 36.0, -10.0, 18.0), (24.0, 4.0))
FLAPS = [(235, 239, 38.0), (165, 167, 52.0)]
for left, right, degrees in FLAPS:
    kit.n.pieced(f"coral_manta_flap_{left}", lambda degrees=degrees: manta_flap(degrees), (72, 56), [
        (f"coral_manta_wing_{left}", LEFT[0], LEFT[1], lambda s=left: kit.sheet_mask("enemy_T", s)),
        (f"coral_manta_wing_{right}", RIGHT[0], RIGHT[1], lambda s=right: kit.sheet_mask("enemy_T", s))])


if __name__ == "__main__":
    vs.v.run()
