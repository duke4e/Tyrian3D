"""The store illustration's generators (batch AU): the pictures the store draws in the middle of
the ship for the generator (store.json "generators"), as models standing on the ship's deck (their
base at z = 0, models.cfg `origin`; au_rear_kit.py has the conventions). Each stands on a pipe
running back down the ship's middle towards the rear gun; their energy glows (emission).

- store_generator_16 (weapon picture 16, 31 x 35): Standard MR-9, Advanced MR-12. A reactor block
  with two glowing blue U-shaped channels.
- store_generator_17 (28 x 29): Gencore Custom MR-12. A steel helmet over a glowing blue visor.
- store_generator_18 (21 x 34): Standard MicroFusion. A tall capsule of blue light in a frame.
- store_generator_19 (22 x 35): Advanced MicroFusion. A steel head and a round body with three
  blue lenses.
- store_generator_20 (29 x 35): Gravitron Pulse-Wave. A sphere of fire in a steel gimbal.

usage: Blender -b --factory-startup -P au_generators.py -- [--only store_generator_16,...]
           [--preview <directory>] [--check] [--refs <store sheets directory>] [--out <directory>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import au_rear_kit as a  # noqa: E402

PICTURES = {
    "store_generator_16": (31, 35, """
5-25
4-26
3-27
2-28
2-28
2-28
2-28
2-28
2-28
2-28
2-28
2-28
2-28
2-28
2-28
2-28
2-28
1-28
1-29
1-29
0-30
0-30
0-30
0-30
0-30
1-29
2-28
3-27
5-25
7-23
7-20
8-20
8-20
8-20
8-20
"""),
    "store_generator_17": (28, 29, """
9-18
8-19
7-20
6-21
5-22
4-23
4-23
4-23
4-23
4-23
4-24
0-27
0-27
0-27
0-27
0-27
1-26
2-25
3-24
3-23
3-23
3-23
3-23
3-23
3-23
4-23
5-22
6-21
5 7-20
"""),
    "store_generator_18": (21, 34, """
8-13
7-14
6-15
5-16
5-16
1-19
0-20
0-20
0-20
0-20
0-20
0-3 5-20
0-20
0-20
0-20
0-3 5-20
0-20
0-20
0-20
0-20
0-20
0-20
0-20
0-20
0-20
0-20
0-20
0-20
0-20
0-20
1-19
2-18
3-16
3-16
"""),
    "store_generator_19": (22, 35, """
0-21
0-21
0-21
0-21
0-21
0-21
0-21
0-21
0-21
0-21
0-21
2-19
4-17
6 9-13
8-13
6-16
5-17
5-17
4-18
2-20
1-21
1-21
1-21
1-21
1-21
1-21
1-21
3-20
4-19
5-18
6-17
7-14
7-14
7-14
7-14
"""),
    "store_generator_20": (29, 35, """
4-24
4-24
4-24
4-24
4-24
4-24
4-24
4-24
4-24
2-26
1-27
0-28
0-28
0-28
1-27
2-26
2-26
2-26
3-25
3-25
3-25
3-25
3-25
3-25
4-24
5-23
8-19
9-18
9-18
10-17
10-18
10-18
10-18
10-18
10-18
"""),
}

# Where the store draws each picture (top-left x, y and size), for the --refs ship preview.
PLACEMENTS = {
    "store_generator_16": (62, 84, 31, 35),
    "store_generator_17": (64, 85, 28, 29),
    "store_generator_18": (67, 86, 21, 34),
    "store_generator_19": (66, 84, 22, 35),
    "store_generator_20": (63, 97, 29, 35),
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


def stalk(v, c0, c1, r0, r1, gold=None):
    """The pipe the generator stands on, down the middle to the rear gun (columns c0-c1, rows
    r0-r1), and gold pipes beside it (gold: their columns' middles)."""
    x = (v.xe(c0) + v.xe(c1 + 1)) / 2
    r = (v.xe(c1 + 1) - v.xe(c0)) / 2
    a.lathe_axis("stalk", (x, v.ye(r0), 1.4), (x, v.ye(r1 + 1) - 0.4, 1.4),
                 [(0, r * 0.8), (0.1, r), (1, r)], M["steel_light"], 16, squash=0.8)
    for r_ in (r0 + 2.0, r0 + 4.6):
        a.cylinder("stalk_band", (x, v.ye(r_), 1.4), (x, v.ye(r_ + 0.8), 1.4), r + 0.25, M["steel_dark"], segments=16,
                   squash=0.8)
    for gx in gold or ():
        a.lathe_axis("gold_pipe", v.at(gx, r0 - 0.5, 1.0), (v.x(gx), v.ye(r1 + 1) - 0.4, 1.0),
                     [(0, 1.2), (0.12, 1.6), (1, 1.6)], M["gold"], 10)


def generator_16():
    """Standard MR-9 and Advanced MR-12 (picture 16, 31 x 35): a reactor block with a raised
    middle and two vented shoulders at the front, two glowing blue U-shaped channels behind them
    with a bright band between, standing on its pipe."""
    p = a.Picture(PICTURES["store_generator_16"])
    v = p.view()
    a.slab("body", v.outline(rows=(0, 27), epsilon=1.0), -1.5, 2.2, M["steel_mid"], bevel=1.0, segments=2)
    a.block("middle", v.xe(9.4), v.xe(21.6), v.ye(0), v.ye(10.6), -0.5, 5.2, M["steel_light"], 1.0, 3)
    a.block("middle_top", v.xe(11), v.xe(20), v.ye(1.6), v.ye(9.2), 4.6, 5.6, M["steel"], 0.4)
    left = []
    left.append(a.block("shoulder", v.xe(2.2), v.xe(9.6), v.ye(0.8), v.ye(11.4), -0.5, 4.4, M["steel"], 1.4, 3))
    left.append(a.block("vent", v.xe(3.8), v.xe(8.6), v.ye(4.6), v.ye(10.4), 3.4, 4.7, M["black"], 0.3))
    for r in (6.2, 8.2):
        left.append(a.block("vent_slat", v.xe(3.6), v.xe(8.8), v.ye(r), v.ye(r + 0.6), 3.5, 4.6, M["steel_mid"], 0.0))
    # Blue dots beside the channels (columns 4-6, rows 18-20) and in the band (columns 7-8).
    left.append(a.ellipsoid("dot", v.at(5.0, 19.0, 2.6), (1.3, 1.4, 1.0), M["energy"], 10, 6))
    left.append(a.ellipsoid("dot", v.at(7.6, 22.4, 3.6), (1.0, 1.0, 0.8), M["energy"], 10, 6))
    mirrored(left, v.xe(15.5))
    # The upper channel: a U of blue energy in a dark trough (rows 12-20).
    upper = path(v, [(6.4, 12.0), (6.8, 14.2), (8.4, 16.4), (11.2, 17.6), (15.5, 17.9), (19.8, 17.6), (22.6, 16.4),
                     (24.2, 14.2), (24.6, 12.0)], [3.0, 2.8, 2.6, 2.5, 2.5, 2.5, 2.6, 2.8, 3.0])
    a.tube("trough", [(x, y, z - 0.6) for x, y, z in upper], 2.2, M["black"], 10,
           radii=[1.6, 2.2, 2.7, 3.0, 3.1, 3.0, 2.7, 2.2, 1.6], squash=0.7)
    a.tube("channel", upper, 1.8, M["energy"], 12, radii=[1.1, 1.6, 2.1, 2.4, 2.5, 2.4, 2.1, 1.6, 1.1], squash=0.75)
    a.ellipsoid("channel_hot", v.at(10.4, 16.2, 4.2), (1.4, 0.9, 0.5), M["energy_hot"], 10, 6)
    # The bright band (rows 20-23) and the lower channel (rows 22-26).
    a.block("band", v.xe(0.6), v.xe(30.4), v.ye(20.2), v.ye(23.0), -0.5, 3.6, M["steel_light"], 0.9, 2)
    lower = path(v, [(8.0, 22.8), (9.6, 24.6), (12.4, 25.6), (15.5, 25.8), (18.6, 25.6), (21.4, 24.6), (23.0, 22.8)],
                 [3.0, 2.7, 2.6, 2.6, 2.6, 2.7, 3.0])
    a.tube("channel", lower, 1.4, M["energy"], 12, radii=[0.9, 1.3, 1.6, 1.7, 1.6, 1.3, 0.9], squash=0.75)
    stalk(v, 11, 17, 27, 34, gold=(8.6, 20.4))


def generator_17():
    """Gencore Custom MR-12 (picture 17, 28 x 29): a steel helmet over a glowing blue visor, wings
    to the sides, a blue arch below on a dark base."""
    p = a.Picture(PICTURES["store_generator_17"])
    v = p.view()
    a.slab("base", v.outline(rows=(16, 28), epsilon=1.0), -1.5, 2.0, M["steel_dark"], bevel=1.0, segments=2)
    a.slab("wings", v.outline(rows=(10, 16), epsilon=1.0), -1.0, 2.6, M["steel"], bevel=1.0, segments=2)
    left = [a.ellipsoid("wing_tip", v.at(1.6, 11.8, 1.6), (1.8, 1.4, 1.4), M["steel_light"], 12, 6)]
    mirrored(left, v.xe(14))
    # The visor: a thick arch of blue light under the helmet's brow (rows 12-17).
    visor = v.poly([(7.0, 12.2), (20.0, 12.2), (20.0, 17.6), (17.8, 17.6), (17.4, 16.0), (9.6, 16.0), (9.2, 17.6),
                    (7.0, 17.6)])
    a.slab("visor", visor, 0.0, 3.9, M["energy"], bevel=1.2, segments=3)
    shine = path(v, [(9.4, 13.6), (11.0, 13.0), (13.5, 12.8), (15.6, 13.0)], [4.5, 4.7, 4.7, 4.6])
    a.tube("visor_shine", shine, 0.5, M["energy_hot"], 8, radii=[0.2, 0.5, 0.5, 0.2])
    # The helmet (rows 0-11), with a seam to the right of its crown.
    a.dome("helmet", v.xe(14), v.ye(6.2), 1.0, 9.6, 6.2, 4.4, M["steel"], 28, 8, skirt=2.0)
    a.dome("helmet_crown", v.xe(14), v.ye(5.0), 4.2, 3.6, 3.0, 1.3, M["steel_light"], 16, 5)
    seam = path(v, [(17.6, 1.6), (18.0, 4.0), (18.0, 7.0), (17.6, 9.6)], [3.8, 4.8, 4.8, 3.8])
    a.tube("seam", seam, 0.35, M["black"], 6)
    # The blue arch (rows 20-23) round a dark core.
    arch = path(v, [(9.0, 23.8), (9.0, 21.8), (10.6, 20.8), (13.5, 20.6), (16.4, 20.8), (18.0, 21.8), (18.0, 23.8)],
                [2.4, 2.8, 3.0, 3.0, 3.0, 2.8, 2.4])
    a.tube("arch", arch, 1.2, M["energy"], 10, radii=[1.0, 1.2, 1.3, 1.3, 1.3, 1.2, 1.0], squash=0.8)
    a.block("arch_core", v.xe(11.6), v.xe(15.6), v.ye(21.4), v.ye(25), 0.0, 2.8, M["steel_mid"], 0.4)


def generator_18():
    """Standard MicroFusion (picture 18, 21 x 34): a tall capsule of blue light in a steel frame,
    side rails with red panels, gold feet and the pipe below."""
    p = a.Picture(PICTURES["store_generator_18"])
    v = p.view()
    a.slab("base", v.outline(rows=(2, 30), epsilon=1.0), -1.5, 1.4, M["steel_mid"], bevel=0.8, segments=2)
    cx = v.xe(10.5)
    a.lathe_axis("core", (cx, v.ye(3.0), 2.6), (cx, v.ye(24.0), 2.6),
                 [(0, 0.0), (0.06, 2.6), (0.14, 3.3), (0.86, 3.3), (0.94, 2.6), (1, 0.0)], M["energy"], 20, squash=0.9)
    a.lathe_axis("core_hot", (v.xe(9.6), v.ye(5.4), 4.6), (v.xe(9.6), v.ye(13.0), 4.6),
                 [(0, 0.0), (0.2, 0.7), (0.8, 0.7), (1, 0.0)], M["energy_hot"], 8, squash=0.6)
    a.block("cap", v.xe(5.2), v.xe(15.8), v.ye(0), v.ye(4.4), -0.5, 5.4, M["steel_light"], 1.4, 3)
    a.block("foot_block", v.xe(5.6), v.xe(15.4), v.ye(22.6), v.ye(25.4), -0.5, 4.6, M["steel"], 0.8)
    left = []
    left.append(a.block("frame", v.xe(5.0), v.xe(7.2), v.ye(3.0), v.ye(24.0), -0.5, 4.4, M["steel_light"], 0.6))
    left.append(a.block("rail", v.xe(0.2), v.xe(4.6), v.ye(4.6), v.ye(30.4), -0.5, 3.2, M["steel"], 1.0, 2))
    left.append(a.block("rail_panel", v.xe(1.4), v.xe(3.8), v.ye(10.6), v.ye(18.6), 2.0, 3.6, M["red"], 0.4))
    left.append(a.cylinder("pipe", v.at(4.6, 5.0, 2.0), v.at(4.6, 23.0, 2.0), 0.55, M["gold_dark"], segments=8))
    foot = v.poly([(0.6, 23.8), (6.2, 23.8), (7.2, 34), (2.8, 34), (0.6, 30)])
    left.append(a.slab("foot", foot, -1.0, 2.8, M["gold"], bevel=0.8, segments=2))
    mirrored(left, cx)
    stalk(v, 7, 13, 25, 33)


def generator_19():
    """Advanced MicroFusion (picture 19, 22 x 35): a steel head with two blue lights and a raised
    middle, a neck with red lamps, a round body with three blue lenses, the pipe below."""
    p = a.Picture(PICTURES["store_generator_19"])
    v = p.view()
    cx = v.xe(11)
    a.slab("head", v.outline(rows=(0, 12), epsilon=1.0), -1.0, 3.4, M["steel"], bevel=1.2, segments=3)
    a.block("head_middle", v.xe(7.2), v.xe(14.8), v.ye(0.4), v.ye(12.6), 0.0, 5.0, M["steel_light"], 1.0, 3)
    left = []
    left.append(a.block("light_frame", v.xe(3.4), v.xe(8.4), v.ye(2.4), v.ye(5.6), 2.0, 3.9, M["steel_dark"], 0.4))
    left.append(a.ellipsoid("light", v.at(5.6, 3.6, 3.7), (2.0, 1.2, 0.8), M["energy"], 12, 6))
    left.append(a.ellipsoid("lamp", v.at(6.4, 13.6, 2.8), (0.7, 0.8, 0.6), M["lamp"], 8, 5))
    mirrored(left, cx)
    a.block("neck", v.xe(6.2), v.xe(15.8), v.ye(12.4), v.ye(15.6), -0.5, 2.6, M["steel_dark"], 0.6)
    a.ellipsoid("lamp", v.at(9.6, 13.4, 2.8), (0.7, 0.8, 0.6), M["lamp"], 8, 5)
    # The body (rows 15-30): a round shell with three lenses.
    a.dome("body", cx, v.ye(22.6), -0.5, 10.4, 8.0, 3.8, M["steel"], 28, 8, skirt=1.0)
    for c, r, radius in ((6.0, 22.4, 3.0), (16.0, 22.4, 3.0), (11.0, 27.0, 2.5)):
        x, y = v.x(c), v.y(r)
        z = 2.4 if r < 25 else 1.8
        a.cylinder("lens_ring", (x, y, 0.5), (x, y, z + 0.4), radius * 1.15 + 0.5, M["steel_light"], segments=18,
                   squash=(radius * 0.85 + 0.5) / (radius * 1.15 + 0.5))
        a.dome("lens", x, y, z + 0.3, radius * 1.15, radius * 0.85, 1.5, M["energy"], 18, 5)
        a.ellipsoid("lens_hot", (x - radius * 0.3, y + radius * 0.25, z + 1.5), (0.8, 0.6, 0.3), M["energy_hot"], 8, 4)
    stalk(v, 7, 13, 30, 34)


def generator_20():
    """Gravitron Pulse-Wave (picture 20, 29 x 35): a sphere of red and gold fire held in a steel
    gimbal, its pivots at the sides, flames glowing under it, the pipe below."""
    p = a.Picture(PICTURES["store_generator_20"])
    v = p.view()
    cx = v.xe(14.5)
    cy = v.ye(11.4)
    a.slab("base", v.outline(rows=(8, 26), keep=lambda c, r: 3 <= c <= 25, epsilon=1.0), -1.5, 0.6, M["steel_dark"],
           bevel=0.6)
    # The glow under the sphere (rows 17-25), wider than its gimbal there.
    a.dome("flames", cx, v.ye(21.4), 0.0, 11.8, 4.4, 2.2, M["fire_dim"], 24, 5, skirt=1.0)
    centre, radii = (cx, cy, 0.6), (9.6, 10.6, 5.4)
    a.dome("sphere", centre[0], centre[1], centre[2], *radii, M["fire"], 56, 14, skirt=1.2)
    a.glow_spot("sphere_spot", centre, radii, (v.x(10.4), v.y(6.6)),
                [(6.4, 0.14, M["fire_warm"]), (4.4, 0.28, M["fire_hot"]), (2.4, 0.42, M["fire_core"])])
    a.glow_spot("sphere_spot_low", centre, radii, (v.x(11.0), v.y(16.4)),
                [(3.8, 0.14, M["fire_warm"]), (2.0, 0.28, M["fire_hot"])])
    # The gimbal: a band over the sphere's outline, pivots at the sides, a chin band in front.
    ring = []
    for i in range(41):
        t = math.pi * (-0.12 + 1.24 * i / 40)  # from the right pivot over the top to the left one
        ring.append((cx + 10.4 * math.cos(t), cy + 11.0 * math.sin(t), 1.6 + 1.4 * math.sin(t)))
    a.tube("gimbal", ring, 1.1, M["steel"], 10, squash=0.9)
    chin = path(v, [(4.6, 15.6), (6.6, 19.6), (10.4, 22.6), (14.5, 23.2), (18.6, 22.6), (22.4, 19.6), (24.4, 15.6)],
                [1.6, 2.6, 3.4, 3.6, 3.4, 2.6, 1.6])
    a.tube("chin", chin, 1.4, M["steel_light"], 10, radii=[1.2, 1.4, 1.6, 1.8, 1.6, 1.4, 1.2], squash=0.85)
    left = [a.lathe_axis("pivot", v.at(0.2, 11.6, 2.0), v.at(5.6, 11.6, 2.0),
                         [(0, 1.6), (0.15, 2.4), (0.7, 2.6), (1, 2.0)], M["steel_light"], 16, squash=0.9)]
    mirrored(left, cx)
    stalk(v, 10, 16, 25, 34, gold=(9.0,))


MODELS = {
    "store_generator_16": generator_16,
    "store_generator_17": generator_17,
    "store_generator_18": generator_18,
    "store_generator_19": generator_19,
    "store_generator_20": generator_20,
}


def build(name):
    M.clear()
    M.update(a.materials())
    MODELS[name]()


if __name__ == "__main__":
    # The ship preview shows each generator with the most common rear gun (store_gun_8).
    gun = (os.path.join(a.OUT_DIR, "store_gun_8.glb"), 41, 92, 73, 50)
    a.run({name: (lambda name=name: build(name)) for name in MODELS},
          {name: a.Picture(spec) for name, spec in PICTURES.items()}, PLACEMENTS, lambda name: gun)
