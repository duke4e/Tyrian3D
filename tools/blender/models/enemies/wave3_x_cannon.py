"""Batch X of wave 3 (sheet C): DELI's and New Deli's long blue cannons, which the level events lay out as four
sprites side by side on the top layer: one pointing right (C 269, 271, 273 and the 1x1 275 at its muzzle)
and its mirror image pointing left (the 1x1 C 238 at its muzzle, 239, 241, 243). The levels turn on the
small enemies' adjustment for them, so the 1x1 muzzle pieces sit exactly where the sheet draws them (the
top half of the row, against the barrel). Modelled whole as the sprites look (models.cfg: yaw=0) and cut
into the sprites' pieces, drawn at their own origins (origin) so they meet; the mirror image is the same
model mirrored.

- deli_cannon_breech, deli_cannon_mount, deli_cannon_barrel, deli_cannon_muzzle (C 269, 271, 273, 275): the
  cannon pointing right: a silver breech with a blue handle curving under it and a finned blue block below
  that, a blue receiver with a raised sight on top, standing on a dark blue trunnion block on a purple
  pedestal, a slimmer barrel with two collars and a loop under it, and a squared muzzle with a rounded cap
  and an orange glow in its port.
- deli_cannon_l_muzzle, deli_cannon_l_barrel, deli_cannon_l_mount, deli_cannon_l_breech (C 238, 239, 241,
  243): the same pointing left.

usage: Blender -b --factory-startup -P wave3_x_cannon.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole cannon|cannon_l --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_x_kit as x  # noqa: E402
from wave3_x_kit import k, w, pal  # noqa: E402

# Whole coordinates: the art CANNON (84 x 28) with its origin at (42, 14): column c, row r at
# x = c - 42 .. c - 41, y = 14 - r - 1 .. 14 - r.
GZ = 12.6        # the gun's axis height (the pedestal under it is 5 high)
GY = 7.2         # the gun's axis across the screen (rows 1-13)


def X(col):
    return col - 42 + 0.5


def Y(row):
    return 14 - row - 0.5


def cannon_mats():
    blue = {s: pal(f"dc_blue{s}", 0x30 | s, metallic=0.5, roughness=0.3) for s in range(2, 13)}
    grey = {s: pal(f"dc_grey{s}", s, metallic=0.65, roughness=0.25) for s in range(3, 13)}
    purple = {s: pal(f"dc_purple{s}", 0x50 | s, metallic=0.3, roughness=0.5) for s in range(2, 9)}
    return blue, grey, purple


def paint_blue(obj, blue, top=9, mid=7, side=5, under=3):
    w.paint_faces(obj, lambda c, n: blue[top] if n.z > 0.85 else blue[mid] if n.z > 0.45 else
                  blue[side] if n.z > -0.3 else blue[under])


def cannon_whole(mirror=False):
    """The cannon pointing right (mirror: pointing left, mirrored about x = 0)."""
    blue, grey, purple = cannon_mats()
    dark = pal("dc_dark", 0x01, metallic=0.3, roughness=0.6)
    glow = pal("dc_glow", 0x79, metallic=0.0, roughness=0.3, glow=2.0)
    glow_core = pal("dc_glow_core", 0x7c, metallic=0.0, roughness=0.3, glow=2.8)

    # The pedestal: a purple block under the mount (cols 25-48, the whole height of the row).
    ped = w.rounded_box("pedestal", (X(36.5), 0.0, 2.5), (23.6, 27.6, 5.0), purple[5], bevel=1.0)
    w.paint_faces(ped, lambda c, n: purple[6] if n.z > 0.8 else purple[3])
    # Its top's dark border round the mount's foot.
    w.rounded_box("pedestal_plate", (X(37.5), Y(17.5), 5.15), (16.4, 17.0, 0.5), purple[3], bevel=0.2, segments=1)

    # The trunnion block: dark blue, from the pedestal up under the gun (cols 31-44, rows 12-24).
    mount = w.rounded_box("mount", (X(37.5), Y(15.5), 7.6), (14.0, 15.0, 6.0), blue[5], bevel=1.0)
    paint_blue(mount, blue, 7, 6, 4, 3)
    w.rounded_box("mount_step", (X(37.5), Y(21.5), 5.9), (11.6, 4.4, 2.6), blue[4], bevel=0.6, segments=1)
    w.lathe_axis("trunnion", [(0.0, 2.4), (15.6, 2.4)], blue[6], (X(29.5), Y(8.5), GZ - 3.4), (1, 0, 0), 16)

    # The breech: a silver cylinder, its rear end rounded (cols 0-21, rows 2-9).
    by, bz, br = Y(5.5), GZ + 0.4, 3.7
    secs = [(-41.6, by, bz, 1.4, 1.4, 1.4), (-41.0, by, bz, 2.6, 2.6, 2.6), (-40.0, by, bz, 3.3, 3.3, 3.3),
            (-38.8, by, bz, br, br, br), (-21.4, by, bz, br, br, br), (-21.0, by, bz, br - 0.3, br - 0.3, br - 0.3)]
    breech = x.t.loft_x("breech", secs, grey[8], segments=28)
    w.paint_faces(breech, lambda c, n: grey[11] if n.z > 0.9 else grey[9] if n.z > 0.5 else grey[6] if n.z > -0.2
                  else grey[4])
    for xx in (-24.6, -23.2):
        w.lathe_axis(f"breech_ring{xx}", [(-0.3, br), (-0.15, br + 0.35), (0.15, br + 0.35), (0.3, br)], grey[5],
                     (xx, by, bz), (1, 0, 0), 28)
    # The blue handle under it, its rear end curving up into the breech's end (rows 9-12).
    hy = Y(10.8)
    path = [(-20.0, hy, GZ - 2.6), (-30.0, hy, GZ - 2.8), (-37.5, hy, GZ - 2.6), (-40.2, hy + 1.2, GZ - 1.2),
            (-40.4, by - 0.8, GZ + 0.2)]
    handle = w.tube("handle", x.catmull(path, 0.7), 1.55, blue[8], 14)
    paint_blue(handle, blue, 10, 8, 6, 4)
    # The finned block below (cols 7-19, rows 13-18): blue, five dark slots across its top.
    fin_block = w.rounded_box("fin_block", (X(13.0), Y(15.6), GZ - 4.8), (12.6, 5.8, 4.0), blue[6], bevel=0.8)
    paint_blue(fin_block, blue, 8, 7, 5, 3)
    for i in range(5):
        xx = X(9.0 + 2.2 * i)
        w.rounded_box(f"fin_slot{i}", (xx, Y(16.0), GZ - 2.8), (0.8, 4.6, 0.9), dark, bevel=0.2, segments=1)

    # The receiver: a boxy blue hull from the breech to the barrel (cols 21-50).
    secs = [(X(20.6), GY + 0.2, GZ, 4.4, 4.2, 4.0), (X(21.2), GY + 0.2, GZ, 5.4, 4.8, 4.4),
            (X(27.6), GY + 0.2, GZ, 5.6, 4.8, 4.4), (X(28.2), GY - 0.4, GZ, 4.8, 4.2, 4.0),
            (X(29.0), GY - 0.2, GZ, 5.6, 5.0, 4.6), (X(48.5), GY - 0.2, GZ, 5.6, 5.0, 4.6),
            (X(50.0), GY + 0.4, GZ, 4.4, 4.2, 4.0)]
    receiver = x.t.loft_x("receiver", secs, blue[7], segments=32, power=4.0)
    paint_blue(receiver, blue, 9, 7, 5, 3)
    # The raised sight on top (cols 33-42, rows 0-3) and a lighter plate in front of it.
    sight = w.rounded_box("sight", (X(37.5), Y(2.4), GZ + 5.4), (10.4, 5.2, 2.6), blue[8], bevel=0.7)
    paint_blue(sight, blue, 10, 8, 6, 4)
    w.rounded_box("sight_glass", (X(37.5), Y(1.2), GZ + 6.8), (6.0, 1.6, 0.4), blue[11], bevel=0.15, segments=1)
    for i, col in enumerate((24.0, 45.5)):
        w.rounded_box(f"rivet_plate{i}", (X(col), GY + 1.0, GZ + 4.75), (3.0, 4.2, 0.6), blue[9], bevel=0.25,
                      segments=1)

    # The barrel: slimmer, two collars on it and a loop under it (cols 50-66).
    ay = Y(5.4)
    w.lathe_axis("barrel", [(0.0, 3.4), (16.6, 3.1)], blue[7], (X(49.5), ay, GZ + 0.6), (1, 0, 0), 24)
    for col in (52.6, 58.4):
        c = w.lathe_axis(f"collar{col}", [(-0.9, 3.4), (-0.6, 4.0), (0.6, 4.0), (0.9, 3.4)], blue[9],
                         (X(col), ay, GZ + 0.6), (1, 0, 0), 24)
        paint_blue(c, blue, 10, 9, 6, 4)
    loop = [(X(53.0), ay - 3.0, GZ - 1.6), (X(53.8), Y(11.6), GZ - 3.4), (X(55.6), Y(12.4), GZ - 3.8),
            (X(57.4), Y(11.6), GZ - 3.4), (X(58.0), ay - 3.0, GZ - 1.6)]
    w.tube("loop", x.catmull(loop, 0.6), 0.85, blue[8], 10)

    # The muzzle: a squared housing (cols 61-77), its cap rounded, an orange glow in the dark port on its lower
    # side (cols 64-71, rows 8-10).
    my = Y(6.6)
    mz = GZ + 0.6
    secs = [(X(60.8), my + 0.6, mz, 3.6, 3.6, 3.6), (X(61.6), my, mz, 5.4, 4.6, 4.2),
            (X(72.4), my, mz, 5.4, 4.6, 4.2), (X(72.9), my, mz, 4.6, 3.9, 3.6),
            (X(73.4), my, mz, 5.4, 4.8, 4.4), (X(76.0), my, mz, 5.4, 4.6, 4.2),
            (X(77.2), my, mz, 4.2, 3.6, 3.4), (X(77.8), my, mz, 2.2, 2.0, 2.0)]
    muzzle = x.t.loft_x("muzzle", secs, blue[8], segments=32, power=3.0)
    paint_blue(muzzle, blue, 10, 8, 6, 4)
    pz = mz + 3.6
    w.rounded_box("port_hole", (X(67.6), Y(9.3), pz), (8.4, 3.0, 1.6), dark, bevel=0.5, segments=1)
    w.sphere("port_glow", (X(67.4), Y(9.3), pz + 0.55), (3.4, 1.25, 0.5), glow, 14, 6)
    w.sphere("port_core", (X(66.8), Y(9.2), pz + 0.85), (1.3, 0.7, 0.35), glow_core, 10, 5)
    # The bore at the cap's end.
    w.lathe_axis("bore", [(-0.6, 1.4), (0.2, 1.4), (0.25, 0.01)], dark, (X(77.8), my, mz), (1, 0, 0), 14)

    if mirror:
        x.bake()
        x.mirror_x(x.meshes(), 0.0)


x.whole("cannon", (84, 28))(lambda: cannon_whole(False))
x.whole("cannon_l", (84, 28))(lambda: cannon_whole(True))

# (name, sprite, large, box (x0, x1, y0, y1) in the whole's coordinates, the sprite's centre)
PIECES = [
    ("deli_cannon_breech", 269, True, False, (-42.0, -18.0, -14.0, 14.0), (-30.0, 0.0)),
    ("deli_cannon_mount", 271, True, False, (-18.0, 6.0, -14.0, 14.0), (-6.0, 0.0)),
    ("deli_cannon_barrel", 273, True, False, (6.0, 30.0, -14.0, 14.0), (18.0, 0.0)),
    ("deli_cannon_muzzle", 275, False, False, (30.0, 42.0, 0.0, 14.0), (36.0, 7.0)),
    ("deli_cannon_l_muzzle", 238, False, True, (-42.0, -30.0, 0.0, 14.0), (-36.0, 7.0)),
    ("deli_cannon_l_barrel", 239, True, True, (-30.0, -6.0, -14.0, 14.0), (-18.0, 0.0)),
    ("deli_cannon_l_mount", 241, True, True, (-6.0, 18.0, -14.0, 14.0), (6.0, 0.0)),
    ("deli_cannon_l_breech", 243, True, True, (18.0, 42.0, -14.0, 14.0), (30.0, 0.0)),
]


def cannon_piece(mirror, box, centre):
    cannon_whole(mirror)
    x.bake()
    x.cut(x.meshes(), box, centre)
    x.budget(4800)
    x.report()


for _name, _sprite, _large, _mirror, _box, _centre in PIECES:
    x.model(_name, [(_sprite, _large)], (24, 28) if _large else (12, 14))(
        lambda m=_mirror, b=_box, c=_centre: cannon_piece(m, b, c))


if __name__ == "__main__":
    x.run()
