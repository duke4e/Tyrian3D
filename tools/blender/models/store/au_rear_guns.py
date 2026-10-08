"""The store illustration's rear guns (batch AU): the pictures the store draws on the back half of
the ship for the rear weapon (store.json "rear" entries), as models standing on the ship's deck
(their base at z = 0, models.cfg `origin`; au_rear_kit.py has the conventions):

- store_gun_8 (weapon picture 8, 73 x 50): Starburst, Rear Mega Pulse, Guided Micro Bombs, Heavy
  Guided Bombs. A steel yoke: two forward prongs with red cowls on its shoulders, blue glass in
  their flanks, a blue glass dome between gold brackets in the middle, three round pods behind.
- store_gun_9 (99 x 50): Multi-Cannon (rear), Rear Heavy Missile Launcher. The same yoke with bare
  steel prongs, cannons slanting out from the shoulders and a gold missile rack in the middle.
- store_gun_10 (55 x 30): Sonic Wave. A crescent of steel horns round a glowing red bowl.
- store_gun_11 (69 x 40): Protron (rear), Scatter Wave. Two steel pods with blue glass on their inner
  faces, joined by a bridge, hoops behind them.
- store_gun_13 (76 x 49): Vulcan Cannon (rear), HotDog Rear. The bridge and hoops of 11 with two
  rotary cannons and red lamps.
- store_gun_15 (70 x 64): Fireball, Banana Blast Rear. The glowing bowl of 10, larger, between two
  tall segmented blades.

usage: Blender -b --factory-startup -P au_rear_guns.py -- [--only store_gun_8,...]
           [--preview <directory>] [--check] [--refs <store sheets directory>] [--out <directory>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import au_rear_kit as a  # noqa: E402
from mathutils import Vector  # noqa: E402

PICTURES = {
    "store_gun_8": (73, 50, """
10-12 14-15 57-58
8-15 57-63
7-15 57-65
6-15 57-66
6-15 57-67
5-15 57-67
5-15 57-68
5-15 57-68
5-15 57-68
5-15 57-68
5-15 57-68
5-15 57-68
5-15 57-68
5-15 57-68
5-15 57-68
5-15 57-68
5-15 57-68
4-15 57-69
3-15 57-69
3-15 57-70
3-15 57-70
2-15 57-70
2-16 56-71
2-16 56-71
2-16 56-71
2-16 56-71
2-71
3-70
3-70
3-70
3-70
3-70
2-71
1-72
1-72
1-72
1-72
1-72
1-72
1-72
2-71
3-70
4-68
7-66
9-64
13-59
14-58
15-57
16-25 30-42 47-56
17-25 31-41 47-55
"""),
    "store_gun_9": (99, 50, """
28-29 71-72
27-29 71-73
26-29 71-74
25-29 71-74
25-29 71-75
24-29 71-75
24-29 71-76
23-29 71-77
23-29 71-77
22-29 71-78
21-29 71-79
21-29 71-79
21-29 71-79
21-29 71-79
7-10 21-29 71-79 90-93
6-11 21-29 71-79 89-94
4-12 22-29 71-78 88-96
3-13 22-29 71-78 87-97
2-14 22-29 71-78 86-98
1-15 22-29 71-78 85-98
1-16 22-29 71-78 84-98
1-16 22-29 71-78 84-98
2-16 22-30 70-78 84-98
3-16 23-30 70-77 84-97
4-17 23-30 70-77 83-96
5-18 22-30 70-78 82-95
6-19 22-78 81-94
7-19 22-78 81-93
8-19 22-78 81-92
9-91
12-88
13-87
14-86
15-85
16-84
17-83
17-83
17-83
17-83
18-82
19-81
20-80
21-79
22-78
22-78
27-73
28-72
29-71
30-39 44-56 61-70
31-39 45-55 61-69
"""),
    "store_gun_10": (55, 30, """
2-4 50-52
2-4 50-52
1-4 50-53
1-4 50-53
0-4 17-38 50-54
0-4 15-40 50-54
0-4 13-42 50-54
0-4 12-43 50-54
0-4 11-43 50-54
0-5 7-46 50-54
0-54
0-54
0-54
0-54
0-54
0-54
0-54
1-53
1-53
1-52
2-52
3-51
4-50
5-49
6-48
7-47
8-46
10-44
11-43
23-31
"""),
    "store_gun_11": (69, 40, """
5-12 16-18 51-53 57-62
5-12 16-18 51-53 57-63
4-18 51-64
4-18 51-65
3-18 51-66
3-18 51-66
3-18 51-66
2-18 51-67
2-18 51-67
2-18 51-67
2-18 51-67
2-18 51-67
1-18 51-68
1-18 51-68
1-18 51-68
1-18 51-68
1-18 51-68
1-18 51-68
1-18 51-68
1-18 51-68
1-18 29-39 51-68
1-18 27-41 51-68
1-19 26-41 50-68
1-68
1-68
1-68
1-68
1-68
1-68
2-67
3-9 19-50 60-66
3-8 20-49 61-66
3-8 21-48 61-66
4-9 21-48 60-65
5-10 20-49 59-64
6-63
7-45 47-62
9-21 24-44 48-60
25-43
26-42
"""),
    "store_gun_13": (76, 49, """
3-11 13-21 55-63 65-73
3-11 13-21 55-63 65-73
1-23 53-75
1-23 53-75
1-23 53-75
1-23 53-75
1-23 53-75
1-23 53-75
1-23 53-75
3-23 55-75
3-21 55-73
3-21 55-73
3-21 55-73
3-21 55-73
3-21 55-73
3-21 55-73
3-21 55-73
3-21 55-73
2-22 54-74
1-23 53-75
1-23 53-75
1-23 53-75
1-23 53-75
1-23 53-75
1-23 53-75
1-23 53-75
1-23 53-75
1-23 53-75
1-23 33-43 52-75
1-24 31-45 51-75
1-25 30-45 50-75
1-75
1-75
1-75
1-75
2-74
2-74
3-73
4-13 23-54 64-71
5-12 24-53 65-70
6-12 25-52 65-70
6-13 25-52 64-69
7-8 10-14 24-53 63-68
8-67
9-49 51-66
10-25 28-49 52-64
28-48
29-47
30-46
"""),
    "store_gun_15": (70, 64, """
9-11 59-61
8-11 59-62
8-11 59-62
7-11 59-63
7-11 59-63
6-11 59-64
6-11 59-64
5-11 59-65
5-11 59-65
4-11 59-66
4-11 59-66
3-11 59-67
3-11 59-67
3-11 59-67
2-11 59-68
2-11 59-68
2-11 59-68
1-11 59-69
1-11 59-69
1-11 59-69
2-11 59-68
2-11 59-68
2-11 59-68
2-11 59-68
2-11 59-68
2-11 59-68
2-11 59-68
2-11 59-68
2-11 59-68
2-11 59-68
2-11 59-68
1-11 59-69
1-11 59-69
1-11 59-69
1-11 59-69
1-11 33-38 59-69
1-11 25-46 59-69
5-11 23-48 59-65
5-11 21-50 59-65
4-11 20-50 59-66
4-11 19-50 59-66
4-12 19-51 58-66
4-13 19-51 57-66
4-66
4-66
4-66
4-66
4-66
4-66
4-66
5-65
5-65
6-64
7-63
9-61
11-59
12-58
13-57
14-56
15-55
16-54
18-52
19-51
31-39
"""),
}

# Where the store draws each picture (top-left x, y and size), for the --refs ship preview.
PLACEMENTS = {
    "store_gun_8": (41, 92, 73, 50),
    "store_gun_9": (27, 92, 99, 50),
    "store_gun_10": (49, 113, 55, 30),
    "store_gun_11": (43, 102, 69, 40),
    "store_gun_13": (39, 96, 76, 49),
    "store_gun_15": (41, 76, 70, 64),
}

M = {}


def mirrored(parts, dx=0.0):
    """Mirror images of the left side's parts across x = dx (the right side)."""
    out = []
    for o in parts:
        copy = a.mirror(o)
        copy.data.transform(a.Matrix.Translation((2 * dx, 0, 0)))
        out.append(copy)
    return out


def path(v, points, z):
    """Pixel-centre points [(column, row)] of view v to model points at heights z (one per point,
    or one for all)."""
    zs = z if isinstance(z, (list, tuple)) else [z] * len(points)
    return [v.at(c, r, h) for (c, r), h in zip(points, zs)]


# --- Pictures 8 and 9: the yoke ----------------------------------------------------------------

def yoke(p, oc=0, flank="glass", centre="dome", shoulder_keep=None):
    """The yoke of pictures 8 and 9, in picture 8's columns and rows (oc: the column of picture p
    that is picture 8's column 0): the shoulders under the prongs, the wide bridge, gold brackets
    and three round pods behind. flank "glass" puts blue glass in the shoulders' flanks; centre
    "dome" a blue glass dome in a gold collar, "rack" a rack of gold missiles."""
    v = p.view(oc)
    Xe, ye = v.xe, v.ye
    dx = v.xe(36.5)  # the yoke's middle
    parts = []
    # The bridge: a deep plate in the outline of rows 26-42, reaching down to the hull's sides.
    bridge = v.outline(cols=(0, 72), rows=(26, 42), epsilon=1.2)
    parts.append(a.slab("bridge", bridge, -6.0, 1.2, M["steel_mid"], bevel=0.9))
    # Its upper deck between the shoulders, a step higher.
    parts.append(a.block("bridge_deck", Xe(14), Xe(59), ye(26) - 0.2, ye(34), -1.0, 2.4, M["steel"], 0.7))
    left = []
    # The shoulder: a rounded block under the prong (columns 1-21, rows 17-42).
    shoulder = v.outline(cols=(0, 21), rows=(17, 42), epsilon=1.2, keep=shoulder_keep)
    left.append(a.slab("shoulder", shoulder, -7.0, 2.2, M["steel_mid"], bevel=1.2, segments=3))
    # Its bright top under the prong (rows 17-22), and the housing behind it.
    x0 = 2.6 if flank == "glass" else 7.8
    left.append(a.block("shoulder_top", Xe(x0), Xe(16.2), ye(16.6), ye(22.6), -1.0, 5.6, M["steel_light"], 1.0, 3))
    left.append(a.block("shoulder_housing", Xe(9), Xe(16), ye(22), ye(33), -1.0, 4.4, M["steel"], 0.8))
    left.append(a.block("shoulder_strip", Xe(10), Xe(12.6), ye(24.5), ye(31.5), 3.0, 5.0, M["steel_light"], 0.5))
    left.append(a.block("shoulder_inner", Xe(15), Xe(21.6), ye(25), ye(36), -1.0, 3.6, M["steel"], 0.8))
    if flank == "glass":
        # The blue glass capsule in the flank (columns 3-8, rows 22-32), with a steel band.
        gx = (Xe(3) + Xe(9)) / 2
        left.append(a.lathe_axis("flank_glass", (gx, ye(22) + 0.4, 2.2), (gx, ye(33) - 0.2, 2.2),
                                 [(0, 0.0), (0.05, 2.2), (0.14, 3.0), (0.86, 3.0), (0.95, 2.2), (1, 0.0)],
                                 M["glass"], 18))
        left.append(a.cylinder("flank_band", (gx, ye(22) + 0.2, 2.2), (gx, ye(23.2), 2.2), 3.2, M["steel_dark"],
                               segments=18))
    # The knuckle at the shoulder's back corner (columns 1-13, rows 33-42): a drum along the ship.
    kx = (Xe(1) + Xe(14)) / 2
    left.append(a.lathe_axis("knuckle", (kx, ye(32.5), 0.0), (kx, ye(43), 0.0),
                             [(0, 5.4), (0.12, 6.2), (0.7, 6.2), (0.9, 5.4), (1, 3.6)], M["steel_light"], 18,
                             squash=0.78))
    # The rear pod (columns 13-28, rows 39-49): a launch tube, its muzzle at the back.
    px = (Xe(13) + Xe(29)) / 2
    left.append(a.lathe_axis("pod", (px, ye(38), -0.6), (px, ye(49.6), -0.6),
                             [(0, 6.0), (0.45, 6.6), (0.72, 6.3), (0.88, 5.4), (0.97, 4.6), (1, 0.0)],
                             M["steel"], 18, squash=0.6))
    left.append(a.cylinder("pod_muzzle", (px, ye(48.9), -0.6), (px, ye(49.9), -0.6), 3.4, M["black"],
                           segments=18, squash=0.62))
    left.append(a.cylinder("pod_ring", (px, ye(43.4), -0.6), (px, ye(44.4), -0.6), 6.8, M["steel_dark"],
                           segments=20, squash=0.62))
    # A small red lamp at the shoulder's inner edge (rows 36-37, column 16).
    left.append(a.ellipsoid("lamp", (Xe(16.5), ye(37), 2.6), (0.8, 0.9, 0.8), M["lamp"], 8, 5))
    # The gold brackets: an ear at the middle's upper corner and a ribbed claw beside the middle pod.
    if centre == "dome":
        ear = v.poly([(22, 28.6), (23.6, 26.4), (26, 25.9), (33, 25.9), (30.5, 28.2), (27.4, 31.6), (24.2, 31.8)])
        left.append(a.slab("gold_ear", ear, 0.5, 3.9, M["gold"], bevel=0.9, segments=3))
        for c in (21.8, 24.1, 26.4):
            x = Xe(c) + 0.6
            left.append(a.lathe_axis("gold_rib", (x, ye(34.6), 2.6), (x, ye(45), 2.6),
                                     [(0, 0.5), (0.08, 1.15), (0.88, 1.15), (1, 0.4)], M["gold"], 10))
        left.append(a.block("gold_claw_base", Xe(21), Xe(28), ye(35), ye(44.5), -0.5, 2.6, M["gold_dark"], 0.4))
    parts += left + mirrored(left, dx)
    # The middle pod under the dome (columns 30-42, rows 36-49).
    parts.append(a.lathe_axis("middle_pod", (dx, ye(33), 0.8), (dx, ye(50) + 0.1, 0.8),
                              [(0, 5.4), (0.55, 6.0), (0.78, 5.6), (0.9, 4.4), (0.97, 2.4), (1, 0.0)],
                              M["steel_light"], 22, squash=0.86))
    parts.append(a.cylinder("middle_ring", (dx, ye(41.6), 0.8), (dx, ye(42.6), 0.8), 6.2, M["steel_dark"],
                            segments=20, squash=0.88))
    if centre == "dome":
        # The blue glass dome (columns 28-45, rows 26-35) in a gold collar.
        cy = (ye(26) + ye(36)) / 2
        parts.append(a.dome("dome", dx, cy, 2.0, 8.2, 5.0, 5.4, M["glass"], 28, 8, skirt=1.5))
        ring = [(dx + 8.6 * math.cos(t), cy + 5.4 * math.sin(t), 2.2)
                for t in [2 * math.pi * i / 32 for i in range(32)]]
        parts.append(a.tube("dome_collar", ring, 0.9, M["gold"], 8, closed=True))
    return parts


def prong(p, oc=0):
    """Picture 8's prong pointing forward from the left shoulder (its columns 5-15, rows 0-16): a
    steel pylon with a channel down its top, a red cowl along its outer side curling over its
    front, a dark collar at its foot."""
    v = p.view(oc)
    Xe, ye = v.xe, v.ye
    parts = []
    foot, front = ye(17), ye(0)
    pylon = [(Xe(9), foot), (Xe(16), foot), (Xe(16), front), (Xe(13), front), (Xe(9), front - 4.0)]
    parts.append(a.slab("pylon", pylon, -3.0, 5.6, M["steel"], bevel=0.7))
    # Two rails along its top with a dark channel between them.
    rail_out = [(Xe(9) + 0.3, foot + 1.0), (Xe(11.6), foot + 1.0), (Xe(11.6), front - 1.0), (Xe(9) + 0.3, front - 4.6)]
    parts.append(a.slab("pylon_rail", rail_out, 5.0, 7.0, M["steel_light"], bevel=0.45))
    rail_in = [(Xe(13.2), foot + 1.0), (Xe(16) - 0.3, foot + 1.0), (Xe(16) - 0.3, front - 0.4), (Xe(13.2), front - 0.4)]
    parts.append(a.slab("pylon_rail", rail_in, 5.0, 6.4, M["steel"], bevel=0.45))
    parts.append(a.block("pylon_channel", Xe(11.6), Xe(13.2), foot + 1.0, front - 1.5, 4.0, 5.4, M["black"], 0.0))
    # The collar at its foot (rows 14-16).
    parts.append(a.block("collar", Xe(8.6), Xe(16.4), ye(14), ye(17) - 0.3, -3.0, 7.2, M["steel_dark"], 0.5))
    # The red cowl: a nacelle along the outer side, curling in over the pylon's front.
    sections = []
    for y, x0, x1, top in ((foot - 0.6, 4.8, 9.4, 6.8), (ye(12), 4.6, 9.6, 8.2), (ye(6), 4.6, 9.8, 8.8),
                           (ye(4.5), 5.2, 10.4, 9.0), (ye(3.2), 5.8, 11.2, 8.9), (ye(2.2), 6.6, 12.4, 8.6),
                           (ye(1.2), 7.8, 13.0, 8.0), (ye(0.5), 9.0, 13.0, 7.2), (front - 0.05, 10.4, 12.6, 6.0)):
        sections.append(a.section(y, (Xe(x0) + Xe(x1)) / 2, (Xe(x1) - Xe(x0)) / 2, -2.6, top, power=2.8,
                                  segments=16))
    parts.append(a.loft_y("cowl", sections, M["red"]))
    # A steel strake along its foot.
    parts.append(a.block("cowl_strake", Xe(4.6), Xe(9.2), foot - 0.2, ye(10), -3.0, 3.4, M["steel_dark"], 0.5))
    return parts


def spike(p, oc=0):
    """Picture 9's prong (picture 8's columns 7-15, rows 0-16): a steel spike, its inner face
    flat and bright, sloping to a point at the front, and a dark collar at its foot."""
    v = p.view(oc)
    Xe, ye = v.xe, v.ye
    parts = []
    sections = []
    # (row, outer column, top): the spike narrows from 9 pixels at row 13 to 2 at row 0.
    for r, c0, top in ((17, 7.0, 6.2), (13, 7.0, 6.6), (10, 7.2, 6.8), (7, 9.0, 6.4), (4, 11.0, 5.6),
                       (2, 12.6, 4.6), (0.6, 13.6, 3.6), (0, 14.2, 2.6)):
        c1 = 16.0
        sections.append(a.section(ye(r), (Xe(c0) + Xe(c1)) / 2, (Xe(c1) - Xe(c0)) / 2, -2.5, top, power=2.6,
                                  segments=16))
    sections.reverse()
    parts.append(a.loft_y("spike", sections, M["steel"]))
    # A bright edge along its inner face.
    edge = [v.at(14.6, r, z) for r, z in ((16, 6.6), (11, 7.0), (6, 6.2), (2.5, 4.4), (0.4, 2.6))]
    parts.append(a.tube("spike_edge", edge, 0.8, M["steel_light"], 8, radii=[0.9, 0.9, 0.8, 0.6, 0.3]))
    parts.append(a.block("collar", Xe(6.6), Xe(16.4), ye(14), ye(17) - 0.3, -3.0, 7.4, M["steel_dark"], 0.5))
    return parts


def gun_8():
    p = a.Picture(PICTURES["store_gun_8"])
    yoke(p)
    mirrored(prong(p))


def gun_9():
    """The yoke as picture 8's, one pixel right of the middle (picture 9's column 14 is picture
    8's column 0), with spikes, cannons and a rack of gold missiles."""
    p = a.Picture(PICTURES["store_gun_9"])
    oc = 14
    v = p.view(oc)
    dx = v.xe(36.5)
    yoke(p, oc, flank="none", centre="rack", shoulder_keep=lambda c, r: c >= 8 or r >= 35)
    mirrored(spike(p, oc), dx)
    q = p.view()
    left = []
    # The cannon slanting out from the shoulder: a joint in the shoulder, a barrel, a muzzle
    # (picture 9's columns 1-21, rows 14-36).
    base, joint, end = Vector(q.at(18.0, 32.0, 1.6)), Vector(q.at(11.6, 25.4, 2.0)), Vector(q.at(4.6, 17.6, 2.4))
    axis = (end - base).normalized()
    left.append(a.ellipsoid("cannon_joint", tuple(base), (4.4, 4.4, 3.6), M["steel"], 18, 10))
    left.append(a.lathe_axis("cannon_barrel", tuple(base), tuple(joint + axis * 0.6),
                             [(0, 3.6), (0.5, 3.4), (1, 3.3)], M["steel_mid"], 18, squash=0.85))
    left.append(a.cylinder("cannon_band", tuple(joint - axis * 0.6), tuple(joint + axis * 1.0), 4.0,
                           M["steel_dark"], segments=18, squash=0.85))
    left.append(a.lathe_axis("cannon_muzzle", tuple(joint + axis * 0.8), tuple(end),
                             [(0, 4.6), (0.15, 5.0), (0.8, 5.0), (0.92, 4.8), (1, 4.4)], M["steel_light"], 22,
                             squash=0.82))
    left.append(a.cylinder("cannon_bore", tuple(end - axis * 0.6), tuple(end + axis * 0.15), 2.6, M["black"],
                           segments=16, squash=0.82))
    for t in (0.35, 0.65):
        c = joint + (end - joint) * t
        left.append(a.cylinder("cannon_rib", tuple(c - axis * 0.35), tuple(c + axis * 0.35), 5.15, M["steel_dark"],
                               segments=22, squash=0.82))
    mirrored(left, dx)
    # The rack: two bundles of gold missiles (columns 36-48 and 51-63, rows 27-43) lying along the
    # ship, noses to the back, under gold covers, a gold rib between them.
    for side in (-1, 1):
        cx = dx + side * 6.6
        a.block("rack_cradle", cx - 6.2, cx + 6.2, q.ye(30), q.ye(42.6), -1.0, 2.2, M["black"], 0.4)
        for i in range(5):
            u = (i - 2) / 2.0
            x = cx + u * 4.8
            z = 2.6 + 1.6 * (1 - u * u)
            a.lathe_axis("missile", (x, q.ye(30.4), z), (x, q.ye(43.0), z),
                         [(0, 1.3), (0.86, 1.3), (0.95, 1.05), (1, 0.6)], M["gold"], 10)
            a.cylinder("missile_band", (x, q.ye(34.0), z), (x, q.ye(34.8), z), 1.42, M["gold_dark"], segments=10)
        # The cover over the missiles' tails.
        a.block("rack_cover", cx - 6.4, cx + 6.4, q.ye(26.0), q.ye(31.0), -0.5, 5.8, M["gold"], 1.7, 3)
    a.block("rack_rib", dx - 1.2, dx + 1.2, q.ye(28), q.ye(41), -0.5, 5.6, M["gold_dark"], 0.5)


# --- Pictures 10 and 15: the glowing bowl ------------------------------------------------------

def bowl(p, oc=0, orow=0, post=False):
    """The middle of pictures 10 and 15, in picture 10's columns and rows: a glowing red sphere,
    squashed, with a steel visor across its middle (rows 12-21) and a ribbed spine down the
    middle; post: the spine runs on up through the sphere (picture 15)."""
    v = p.view(oc, orow)
    dx = v.xe(27.5)
    parts = []
    # The sphere: its upper half (rows 4-12) glowing, a hot spot at its upper left, its lower half
    # (rows 21-27) dimmer.
    centre, radii = (dx, v.ye(11), 0.0), (16.8, 7.6, 4.6)
    parts.append(a.dome("bowl_top", centre[0], centre[1], centre[2], *radii, M["fire"], 56, 14, skirt=1.0))
    parts += a.glow_spot("bowl_spot", centre, radii, (v.xe(15.6), v.ye(6.6)),
                         [(6.4, 0.18, M["fire_warm"]), (4.0, 0.32, M["fire_hot"]), (2.0, 0.46, M["fire_core"])])
    parts += a.glow_spot("bowl_spot_right", centre, radii, (v.xe(41.0), v.ye(8.6)),
                         [(3.2, 0.18, M["fire_warm"]), (1.6, 0.32, M["fire_hot"])])
    parts.append(a.dome("bowl_bottom", dx, v.ye(22.5), -0.2, 15.8, 5.6, 3.4, M["fire_dim"], 28, 6, skirt=1.0))
    # The visor across the middle, rising in two humps over the sphere.
    visor = v.poly([(5.5, 21.5), (5.5, 13), (16.5, 12.4), (17, 10.6), (22, 10.6), (23, 13), (32.5, 13),
                    (33.5, 10.6), (38.5, 10.6), (39, 12.4), (49.5, 13), (49.5, 21.5), (42, 22.4), (13, 22.4)])
    parts.append(a.slab("visor", visor, -2.0, 5.0, M["steel"], bevel=1.1, segments=3))
    for c0, c1 in ((16.4, 22.6), (32.4, 38.6)):
        parts.append(a.block("visor_hump", v.xe(c0), v.xe(c1), v.ye(10.2), v.ye(18), -1.0, 7.0, M["steel_light"],
                             1.4, 3))
    parts.append(a.block("visor_lip", v.xe(7), v.xe(48), v.ye(19.2), v.ye(21.8), 2.0, 5.6, M["steel_light"], 0.7))
    # The spine down the middle (columns 25-30), ribbed.
    top = 3.0 if post else 12.0
    parts.append(a.block("spine", v.xe(25), v.xe(30.6), v.ye(top), v.ye(29.6), -1.0, 7.4, M["steel"], 0.9, 2))
    for r in (15.0, 17.4, 23.0, 25.4):
        parts.append(a.block("spine_rib", v.xe(24.6), v.xe(31), v.ye(r), v.ye(r + 0.8), 5.6, 7.7, M["steel_dark"], 0.2))
    if post:
        parts.append(a.block("post_cap", v.xe(25.6), v.xe(30), v.ye(3.4), v.ye(9), 5.0, 8.4, M["steel_light"], 0.8))
    return parts


def horn_path():
    """The left horn of picture 10 (pixel centres), from its tip down round to the middle."""
    return ([(3.2, 0.2), (2.6, 3.0), (2.3, 7.0), (2.7, 11.0), (3.8, 15.0), (5.6, 19.0), (8.2, 23.0), (11.6, 26.2),
             (16.0, 28.0), (21.0, 28.6), (27.5, 28.8)],
            [1.0, 1.9, 2.4, 2.7, 3.0, 3.1, 3.0, 2.7, 2.3, 2.0, 1.9],
            [4.6, 4.0, 3.4, 2.9, 2.5, 2.1, 1.8, 1.6, 1.4, 1.3, 1.3])


def gun_10():
    p = a.Picture(PICTURES["store_gun_10"])
    v = p.view()
    bowl(p)
    points, radii, zs = horn_path()
    horn = a.tube("horn", path(v, points, zs), 2.0, M["steel_light"], 14, radii=radii, squash=0.85)
    mirrored([horn])
    # Joints where the horns meet the visor (columns 6-10, rows 9-16).
    joint = a.ellipsoid("horn_joint", v.at(7.6, 13.0, 2.2), (2.6, 3.6, 2.6), M["steel"], 14, 8)
    mirrored([joint])


def gun_15():
    """The bowl of picture 10, one row of columns right and 32 rows down (picture 15's column 8 is
    picture 10's column 0), with its spine as a post, between two tall segmented blades."""
    p = a.Picture(PICTURES["store_gun_15"])
    bowl(p, 8, 32, post=True)
    v = p.view()
    left = []
    # The blade (columns 1-12, rows 0-36): a long curved blade, its ridge near the inner edge,
    # thinning to its outer edge; dark joints between its three segments.
    sections = []
    rows = [0.0, 0.6, 1.5, 3, 5, 7, 9, 11, 14, 17, 20, 24, 28, 32, 35, 37.0]
    for r in rows:
        run = p.run(min(int(r), 36), 0, 12)
        c_out, c_in = run[0], run[1] + 1
        if r < 1.0:
            c_out, c_in = 9.0 + (1.0 - r) * 0.6, 12.0 - (1.0 - r) * 0.8
        sections.append(blade_section(v.ye(r), v.xe(c_out), v.xe(c_in), -1.0, 0.6, 3.8 if r > 2 else 2.2))
    left.append(a.loft_y("blade", sections[::-1], M["steel"], smooth_angle=40))
    edge = path(v, [(10.4, 0.6), (10.3, 6), (10.0, 14), (9.8, 22), (9.9, 30), (10.2, 36.6)], [2.4, 3.9, 4.2, 4.3, 4.3, 4.2])
    left.append(a.tube("blade_edge", edge, 0.9, M["steel_light"], 8, radii=[0.3, 0.7, 0.9, 0.9, 0.9, 0.9]))
    for r in (18.6, 30.6):
        run = p.run(int(r), 0, 12)
        joint = [(v.xe(run[0]) + 0.2, v.ye(r), 0.4), (v.xe((run[0] + run[1]) / 2), v.ye(r), 3.0),
                 (v.xe(run[1] + 1) - 0.9, v.ye(r), 4.0)]
        left.append(a.tube("blade_joint", joint, 0.45, M["black"], 6))
    # Its root (columns 4-13, rows 37-49) and the arm curving from it to the bottom's middle.
    left.append(a.lathe_axis("blade_root", v.at(8.4, 36.0, 1.6), v.at(8.8, 50.0, 1.2),
                             [(0, 3.6), (0.2, 4.6), (0.75, 4.6), (1, 3.8)], M["steel"], 16, squash=0.8))
    arm = path(v, [(8.8, 48.0), (10.6, 53.0), (14.6, 57.4), (20.0, 60.4), (27.0, 61.8), (35.0, 62.2)],
               [1.4, 1.3, 1.2, 1.1, 1.0, 1.0])
    left.append(a.tube("blade_arm", arm, 2.4, M["steel_light"], 12, radii=[3.4, 3.0, 2.6, 2.3, 2.0, 1.9],
                       squash=0.85))
    for r in (41.0, 45.4):
        left.append(a.cylinder("blade_band", v.at(8.5, r, 1.4), v.at(8.5, r + 1.0, 1.4), 4.8, M["steel_dark"],
                               segments=16, squash=0.82))
    mirrored(left, v.xe(35))


def blade_section(y, x_out, x_in, z_bot, z_edge, z_ridge):
    """A blade's cross-section at y: flat underneath, its top rising from the outer edge (x_out,
    z_edge) to a ridge near the inner edge (x_in), which is bevelled. Points run round it."""
    pts = [Vector((x_out, y, z_bot)), Vector((x_in, y, z_bot))]
    for t in (1.0, 0.92, 0.8, 0.62, 0.42, 0.22, 0.08, 0.0):
        f = math.sin(math.pi / 2 * min(t / 0.8, 1.0)) if t <= 0.8 else 1.0 - (t - 0.8) / 0.2 * 0.3
        pts.append(Vector((x_out + (x_in - x_out) * t, y, z_edge + (z_ridge - z_edge) * f)))
    return pts


# --- Pictures 11 and 13: the bridge and hoops --------------------------------------------------

def bridge(p, oc=0, orow=0):
    """The middle of pictures 11 and 13, in picture 11's columns and rows: the bridge between the
    pods (rows 22-29), the round housing in the middle with a hatch on top and a gold nozzle
    behind, bright plates beside it and two hoops under the pods."""
    v = p.view(oc, orow)
    dx = v.xe(34.5)
    parts = []
    parts.append(a.block("bridge", v.xe(16), v.xe(53), v.ye(21.6), v.ye(30), -4.0, 2.6, M["steel_mid"], 1.0, 2))
    # The housing (columns 19-50, rows 20-39).
    cy = v.ye(29.5)
    parts.append(a.dome("housing", dx, cy, -1.0, 10.6, 10.0, 7.2, M["steel"], 28, 8, skirt=2.0))
    ring = [(dx + 5.8 * math.cos(t), v.ye(24.2) + 3.4 * math.sin(t), 5.6 - 0.6 * math.sin(t))
            for t in [2 * math.pi * i / 24 for i in range(24)]]
    parts.append(a.tube("hatch_ring", ring, 0.9, M["steel_light"], 8, closed=True))
    parts.append(a.dome("hatch", dx, v.ye(24.2), 5.0, 5.2, 2.8, 0.9, M["black"], 20, 3))
    parts.append(a.lathe_axis("nozzle", (dx, v.ye(28.6), 6.0), (dx, v.ye(38.2), 2.0),
                              [(0, 1.8), (0.15, 2.6), (0.8, 3.0), (1, 2.6)], M["gold"], 14, squash=0.8))
    parts.append(a.cylinder("nozzle_bore", (dx, v.ye(37.8), 2.0), (dx, v.ye(38.6), 1.85), 1.8, M["black"],
                            segments=12, squash=0.8))
    left = []
    plate = v.poly([(18.6, 22.4), (25.6, 22.4), (26.6, 28.6), (19.6, 29.4)])
    left.append(a.slab("plate", plate, 0.0, 4.4, M["steel_light"], bevel=0.7))
    # The hoop under the pod: a band from the pod's foot round to the housing.
    hoop = path(v, [(5.0, 27.6), (3.6, 30.6), (4.6, 33.6), (7.6, 35.8), (12.6, 36.6), (18.0, 36.4), (21.8, 34.6),
                    (23.2, 31.6), (22.4, 28.6)], [0.6, 0.4, 0.2, 0.1, 0.0, 0.2, 0.5, 0.8, 1.0])
    left.append(a.tube("hoop", hoop, 1.8, M["steel"], 10, radii=[2.6, 2.6, 2.4, 2.0, 1.7, 1.7, 1.9, 2.2, 2.4],
                       squash=0.9))
    parts += left + mirrored(left, dx)
    return parts


def gun_11():
    p = a.Picture(PICTURES["store_gun_11"])
    v = p.view()
    bridge(p)
    left = []
    # The pod (columns 1-18, rows 0-29): a tall rounded block.
    sections = []
    for r, c0, top in ((29.6, 1.0, 4.4), (12.0, 1.0, 5.0), (7.0, 2.0, 5.0), (4.0, 3.0, 4.8), (2.0, 4.0, 4.4),
                       (0.6, 5.0, 3.8), (0.0, 6.0, 3.0)):
        sections.append(a.section(v.ye(r), (v.xe(c0) + v.xe(19)) / 2, (v.xe(19) - v.xe(c0)) / 2, -6.0, top,
                                  power=3.2, segments=20))
    left.append(a.loft_y("pod", sections, M["steel_mid"]))
    # Its outer side's bright rail and ribs.
    left.append(a.block("pod_rail", v.xe(5.6), v.xe(8.8), v.ye(1.2), v.ye(26), 2.0, 5.8, M["steel_light"], 0.7))
    for r in (7.4, 12.6, 17.8, 23.0):
        left.append(a.loft_y("pod_rib", [a.section(v.ye(r + 0.9), (v.xe(1) + v.xe(19)) / 2, (v.xe(19) - v.xe(1)) / 2 + 0.25,
                                                   -6.2, 5.25, power=3.2, segments=20),
                                         a.section(v.ye(r), (v.xe(1) + v.xe(19)) / 2, (v.xe(19) - v.xe(1)) / 2 + 0.25,
                                                   -6.2, 5.25, power=3.2, segments=20)], M["steel_dark"]))
    # The blue glass on its inner face, in two windows, in a frame.
    gx = (v.xe(11) + v.xe(18)) / 2
    left.append(a.block("glass_frame", v.xe(10.4), v.xe(18.8), v.ye(1.4), v.ye(22.6), 0.0, 4.8, M["steel_dark"], 0.6))
    for r0, r1 in ((2.0, 12.8), (13.8, 22.0)):
        left.append(a.lathe_axis("glass", (gx, v.ye(r0), 3.6), (gx, v.ye(r1), 3.6),
                                 [(0, 0.0), (0.08, 2.5), (0.2, 3.2), (0.8, 3.2), (0.92, 2.5), (1, 0.0)],
                                 M["glass"], 18, squash=0.9))
    mirrored(left, v.xe(34.5))


def gatling(v):
    """A rotary cannon (picture 13's columns 1-23, rows 0-37; v: picture 13's grid): a cluster of
    six barrels in a muzzle ring at the front, a clamp, a receiver with a bright spine and four red
    lamps. Returns the parts (left side)."""
    parts = []
    cx, az = v.xe(12.5), 3.0   # the barrels' axis
    # Receiver (rows 18-37).
    sections = []
    for r, c0, c1, top in ((37.6, 3.4, 22.0, 4.0), (35.0, 2.0, 23.6, 5.6), (30.0, 1.0, 24.0, 6.6),
                           (22.0, 1.0, 24.0, 6.8), (18.2, 1.4, 23.6, 6.4)):
        sections.append(a.section(v.ye(r), (v.xe(c0) + v.xe(c1)) / 2, (v.xe(c1) - v.xe(c0)) / 2, -6.5, top,
                                  power=3.0, segments=22))
    parts.append(a.loft_y("receiver", sections, M["steel"]))
    parts.append(a.block("receiver_spine", v.xe(10.2), v.xe(15), v.ye(18.4), v.ye(36), 2.0, 8.0, M["steel_light"],
                         0.9, 2))
    for c, r in ((8.0, 23.0), (16.0, 23.0), (3.4, 31.6), (19.6, 31.6)):
        x, y = v.x(c), v.y(r)
        parts.append(a.cylinder("lamp_socket", (x, y, 4.0), (x, y, 6.7), 2.0, M["black"], segments=14))
        parts.append(a.ellipsoid("lamp", (x, y, 6.6), (1.55, 1.55, 1.1), M["lamp"], 12, 6))
        parts.append(a.ellipsoid("lamp_core", (x - 0.35, y + 0.35, 7.4), (0.6, 0.6, 0.45), M["lamp_core"], 8, 4))
    # Clamp round the barrels (rows 18-20) and the muzzle ring (rows 2-8).
    parts.append(a.lathe_axis("clamp", (cx, v.ye(21.0), az), (cx, v.ye(17.6), az),
                              [(0, 10.6), (0.5, 11.2), (1, 10.6)], M["steel_dark"], 24, squash=0.44))
    parts.append(a.lathe_axis("muzzle_ring", (cx, v.ye(9.4), az), (cx, v.ye(1.6), az),
                              [(0, 10.6), (0.12, 11.6), (0.88, 11.6), (1, 11.0)], M["steel"], 28, squash=0.46))
    parts.append(a.cylinder("muzzle_band", (cx, v.ye(5.8), az), (cx, v.ye(4.8), az), 11.8, M["steel_light"],
                            segments=28, squash=0.47))
    parts.append(a.cylinder("muzzle_face", (cx, v.ye(1.7), az), (cx, v.ye(1.5), az), 9.2, M["black"], segments=24,
                            squash=0.44))
    for i in range(6):
        t = 2 * math.pi * (i + 0.5) / 6
        x, z = cx + 6.4 * math.cos(t), az + 2.6 * math.sin(t)
        parts.append(a.cylinder("barrel", (x, v.ye(18.2), z), (x, v.ye(-0.2), z), 1.5, M["steel_light"], segments=10))
        parts.append(a.cylinder("bore", (x, v.ye(0.0), z), (x, v.ye(-0.4), z), 0.85, M["black"], segments=8))
    parts.append(a.cylinder("barrel_core", (cx, v.ye(18), az), (cx, v.ye(1.0), az), 3.4, M["black"], segments=14,
                            squash=0.8))
    return parts


def gun_13():
    """The bridge and hoops of picture 11, four columns right and eight rows down (picture 13's
    column 4 is picture 11's column 0), with a rotary cannon on each side."""
    p = a.Picture(PICTURES["store_gun_13"])
    bridge(p, 4, 8)
    v = p.view()
    mirrored(gatling(v), p.view(4, 8).xe(34.5))


MODELS = {
    "store_gun_8": gun_8,
    "store_gun_9": gun_9,
    "store_gun_10": gun_10,
    "store_gun_11": gun_11,
    "store_gun_13": gun_13,
    "store_gun_15": gun_15,
}


def build(name):
    M.clear()
    M.update(a.materials())
    MODELS[name]()


if __name__ == "__main__":
    # The ship preview shows the standard generator (store_generator_16) with each gun.
    standard = (os.path.join(a.OUT_DIR, "store_generator_16.glb"), 62, 84, 31, 35)
    a.run({name: (lambda name=name: build(name)) for name in MODELS},
          {name: a.Picture(spec) for name, spec in PICTURES.items()}, PLACEMENTS, lambda name: standard)
