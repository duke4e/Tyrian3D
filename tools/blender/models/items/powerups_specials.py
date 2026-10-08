"""Special weapon pick-ups (values 32101-32106: the special they give): the small grey fighter
(powerups_parts.ship) with the special's effect round it; and the dual MegaLaser's brown orb
(value 32115, and 32141 SDF Main Gun, in ICESECRET):

- pu_repulsor (271): curved field arcs either side of the nose and below the tail (Repulsor)
- pu_pearl_wind (273): three icy pearls with trailing wisps (Pearl Wind)
- pu_soul_of_zinglon (275): the fighter in a glass capsule (Soul of Zinglon)
- pu_attractor (277): four needles pointing in at the fighter, glowing tips (Attractor)
- pu_ice_beam (121): an icy burst over the nose, streaks and sparkles (Ice Beam)
- pu_flare (123): a ring of fire round the fighter (Flare)
- pu_megalaser_dual (3): a brown orb with a dark rim and two glowing blue bars (MegaLaser Dual)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import powerups_parts as p  # noqa: E402
from powerups_parts import k, px, py  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

ICON_123 = (3, """
...........777..........
..........77y77.........
.........77y7y77........
........77y7o7y77.......
........7y7o0o7y7.......
.......77y7o0o7y77......
......77y7o000o7y77.....
.....77yy7o000o7yy77....
....77y7y7o000o7y7y77...
...77y7o77o000o77o7y77..
...7y7o0o7oo0oo7o0o7y7..
...7y7o00oo707oo00o7y7..
...777o00000000000o777..
...77y7o000000000o7y77..
....77y7o0o000o0o7y77...
.....7y7o00o7o00o7y7....
.....77y7ooooooo7y77....
......77y7777777y77.....
.......77yyyyyyy77......
........777777777.......
.........7777777........
""")


def curve(points, samples=8):
    """A smooth path (Catmull-Rom) through points [(x, y, z)], `samples` steps between each two."""
    pts = [Vector(q) for q in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        for s in range(samples):
            t = s / samples
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return out


def at(col, row, z):
    """A point at a sprite position (pixel centres, fractions allowed)."""
    return (px(col), py(row), z)


def mirrored(col):
    """The column mirrored about the fighter's middle (column 12)."""
    return 24 - col


def repulsor():
    """Steel-blue field arcs: a pair either side of the nose (the outer ones long) and a bowl
    under the tail."""
    p.ship()
    field = k.material("field", palette=0x38, metallic=0.55, roughness=0.25, emission=(40, 100, 200),
                       emission_strength=0.45)
    pale = p.glow("field_inner", (90, 160, 240), 1.0, color=(90, 150, 210))
    outer = [(8.5, 3.6), (7.0, 4.6), (5.8, 5.8), (4.9, 7.2), (4.2, 8.7), (3.9, 10.2), (3.9, 11.6)]
    inner = [(9.4, 6.9), (8.6, 8.1), (7.9, 9.4), (7.4, 10.7)]
    for side in (False, True):
        for arc, radius, mat, z in ((outer, 1.1, field, 1.6), (inner, 0.55, pale, 1.9)):
            points = [at(mirrored(c) if side else c, r, z + 0.4 * math.sin(math.pi * i / (len(arc) - 1)))
                      for i, (c, r) in enumerate(arc)]
            path = curve(points)
            radii = [radius * (0.55 + 0.45 * math.sin(math.pi * i / (len(path) - 1))) for i in range(len(path))]
            p.tube("arc", path, radius, mat, 10, radii=radii)
    bowl = [(7.3, 20.4), (8.3, 21.7), (10.0, 22.7), (12.0, 23.1), (14.0, 22.7), (15.7, 21.7), (16.7, 20.4)]
    path = curve([at(c, r, 1.4) for c, r in bowl])
    radii = [1.1 * (0.55 + 0.45 * math.sin(math.pi * i / (len(path) - 1))) for i in range(len(path))]
    p.tube("bowl", path, 1.1, field, 10, radii=radii)
    small = curve([at(c, r, 1.6) for c, r in ((10.8, 20.3), (12.0, 20.6), (13.2, 20.3))], 6)
    p.tube("bowl_inner", small, 0.45, pale, 8)


def pearl_wind():
    """Three icy pearls, each with a steel-blue wisp trailing down from it."""
    p.ship()
    ice = k.material("pearl", palette=0x8a, metallic=0.1, roughness=0.08, emission=(110, 190, 210),
                     emission_strength=0.5)
    wisp = k.material("pearl_wisp", palette=0x3a, metallic=0.3, roughness=0.2, emission=(50, 110, 190),
                      emission_strength=0.7)
    for col, row, trail in ((3.5, 6.2, [(3.5, 9.5), (3.6, 12.0), (3.8, 14.5), (4.0, 16.4)]),
                            (18.5, 8.2, [(18.6, 11.5), (19.0, 14.0), (19.2, 16.2), (19.2, 18.3)]),
                            (9.5, 19.3, [(9.6, 22.4), (9.6, 24.5), (9.4, 26.0), (9.2, 27.3)])):
        x, y = px(col), py(row)
        # Cut like a crystal: few facets, flat-shaded.
        k.smooth(k.ellipsoid("pearl", (x, y, 2.4), (3.7, 3.5, 2.8), ice, 10, 6), 15)
        path = curve([(x, y - 1.0, 1.6)] + [at(c, r, 1.6 - 0.25 * i) for i, (c, r) in enumerate(trail)])
        radii = [2.1 * (1 - i / (len(path) - 1)) ** 1.2 + 0.15 for i in range(len(path))]
        p.tube("wisp", path, 1.0, wisp, 12, radii=radii)


def soul_of_zinglon():
    """The fighter lying in a long capsule (columns 6-18, rows 0-27): a steel-blue cradle with a
    bright rim and pale glowing ends, under a faint glass lid."""
    cradle = k.material("capsule_cradle", palette=0x37, metallic=0.5, roughness=0.25)
    rim = k.material("capsule_rim", palette=0x3c, metallic=0.6, roughness=0.2, emission=(60, 120, 200),
                     emission_strength=0.6)
    light = p.glow("capsule_light", (130, 185, 245), 1.1, color=(170, 210, 240))
    glass = k.material("capsule_glass", palette=0x3d, roughness=0.05, alpha=0.22)
    half_w, y0, y1 = 6.4, py(27) - 0.5, py(0) + 0.5
    caps = [(0.0, 0.0), (0.02, 0.45), (0.06, 0.72), (0.12, 0.9), (0.2, 1.0), (0.8, 1.0), (0.88, 0.9), (0.94, 0.72),
            (0.98, 0.45), (1.0, 0.0)]
    profile = [(y0 + (y1 - y0) * t, half_w * r) for t, r in caps]
    k.smooth(k.lathe("cradle", profile, cradle, 40, axis_x=0.5, axis_z=-0.2, squash=0.32), 60)
    # A bright rim round the cradle: its outline, the lathe's profile on both sides.
    ring = [(0.5 + r, y, 0.0) for y, r in profile[1:-1]] + [(0.5 - r, y, 0.0) for y, r in reversed(profile[1:-1])]
    p.tube("capsule_rim", curve(ring + ring[:1], 4)[:-1], 0.6, rim, 8, closed=True)
    # The capsule's ends glow (the sprite's pale caps above the nose and below the tail).
    for yc in (py(3.2), py(23.6)):
        k.smooth(k.ellipsoid("capsule_light", (0.5, yc, 1.1), (3.6, 2.2, 1.0), light, 20, 10), 70)
    p.ship(z=1.3)
    k.lathe("glass", profile, glass, 40, axis_x=0.5, axis_z=0.4, squash=0.95)


def attractor():
    """Four steel-blue needles pointing in at the fighter from the corners, three with glowing
    tips (pink, orange, lavender)."""
    p.ship()
    steel = k.material("needle", palette=0x38, metallic=0.6, roughness=0.25, emission=(30, 70, 140),
                       emission_strength=0.4)
    pink = p.glow("tip_pink", (255, 110, 100), 1.2, color=(235, 150, 140))
    orange = p.glow("tip_orange", (255, 140, 20), 1.6, color=(250, 170, 40))
    lavender = p.glow("tip_lavender", (190, 140, 230), 1.1, color=(190, 170, 205))
    needles = (
        ([(0.4, 1.0), (6.6, 7.4)], pink),
        ([(21.8, 1.2), (17.0, 9.6)], None),
        ([(21.8, 27.0), (18.9, 19.0)], orange),
        ([(0.4, 26.0), (7.6, 20.6)], lavender),
    )
    for points, tip in needles:
        (c0, r0), (c1, r1) = points
        path = [at(c0 + (c1 - c0) * t, r0 + (r1 - r0) * t, 1.6) for t in [i / 12 for i in range(13)]]
        radii = [0.6 + 0.5 * i / (len(path) - 1) for i in range(len(path))]
        p.tube("needle", path, 1.0, steel, 10, radii=radii)
        if tip is not None:
            end = path[-1]
            k.smooth(k.ellipsoid("tip", tuple(end), (1.15, 1.15, 1.0), tip, 14, 8), 60)


def ice_beam():
    """An icy burst over the nose: a pale glowing lump with crystal shards, streaks of ice down
    both sides of the nose and loose sparkles."""
    p.ship()
    ice = k.material("ice", palette=0x3e, metallic=0.1, roughness=0.08, emission=(150, 200, 240),
                     emission_strength=0.8)
    shard = k.material("ice_shard", palette=0x3c, metallic=0.2, roughness=0.05, emission=(110, 170, 230),
                       emission_strength=0.6)
    streak = p.glow("ice_streak", (130, 190, 255), 1.6, color=(100, 160, 220))
    sparkle = p.glow("ice_sparkle", (210, 240, 255), 3.0, color=(220, 245, 255))
    x, y = px(12), py(1.8)
    k.smooth(k.ellipsoid("burst", (x, y, 2.4), (3.2, 2.6, 2.2), ice, 24, 14), 80)
    for dx, dy, size, turn in ((-2.6, 0.6, 1.4, 20), (2.5, 1.0, 1.3, -25), (0.0, 2.6, 1.2, 0), (-1.6, -1.8, 1.0, 40),
                               (1.8, -1.6, 1.0, -35)):
        crystal = p.star4("shard", 0, 0, size, size * 0.55, size * 1.2, shard, turn)
        crystal.data.transform(Matrix.Translation((x + dx, y + dy, 3.0)))
    for side in (False, True):
        cols = [(10.0, 5.2), (9.3, 6.6), (8.7, 8.2), (8.3, 9.8), (8.1, 11.4)]
        path = curve([at(mirrored(c) if side else c, r, 1.8) for c, r in cols])
        radii = [0.5 * (1 - 0.6 * i / (len(path) - 1)) for i in range(len(path))]
        p.tube("streak", path, 0.5, streak, 8, radii=radii)
    for col, row, size in ((17.0, 4.0, 1.0), (7.0, 5.0, 0.9), (18.0, 9.0, 0.9), (6.0, 10.0, 1.0)):
        star = p.star4("sparkle", px(col), py(row), size, size * 0.3, 0.5, sparkle)
        star.data.transform(Matrix.Translation((0, 0, 2.2)))


def flare():
    """A ring of fire round the fighter: red flames with a yellow-hot inner line."""
    red = p.glow("flare", (255, 40, 0), 1.6, color=(210, 30, 0))
    yellow = p.glow("flare_hot", (255, 210, 70), 3.2, color=(255, 220, 90))
    p.emblem("flare", ICON_123, "7y", -0.2, 1.6, red, bevel=0.5, smoothing=2, on_orb=False, lift=0.0, min_area=3.0)
    p.emblem("flare_hot", ICON_123, "y", 0.4, 2.2, yellow, bevel=0.35, smoothing=1, on_orb=False, lift=0.0,
             min_area=0.5)
    p.ship(z=0.4)


def megalaser_dual():
    """A brown orb with a dark rim and two glowing blue bars in dark slots (columns 8-10 and 14-16,
    rows 6-20)."""
    p.orb(p.RAMP_BROWN, shade=8, rim=0xe1)
    slot = k.material("bar_slot", palette=0xe2, metallic=0.3, roughness=0.4)
    blue = p.glow("bar", (40, 90, 255), 2.2, color=(40, 81, 235))
    pale = p.glow("bar_core", (160, 210, 255), 3.0, color=(170, 215, 250))
    for col in (9, 15):
        x = px(col)
        y0, y1 = py(20) - 0.2, py(6) + 0.2
        p.conform(k.slab("slot", [(x - 1.9, y0 - 0.4), (x + 1.9, y0 - 0.4), (x + 1.9, y1 + 0.4), (x - 1.9, y1 + 0.4)],
                         -1.2, 0.4, slot, bevel_width=0.5), lift=0.0)
        caps = [(0.0, 0.0), (0.05, 0.7), (0.12, 0.95), (0.2, 1.0), (0.8, 1.0), (0.88, 0.95), (0.95, 0.7), (1.0, 0.0)]
        bar = k.lathe("bar", [(y0 + (y1 - y0) * t, 1.5 * r) for t, r in caps], blue, 16, axis_x=x, squash=0.8)
        p.conform(bar, lift=0.5)
        k.smooth(bar, 50)
        core = k.lathe("bar_core", [(y0 + 1.5 + (y1 - y0 - 3.0) * t, 0.6 * r) for t, r in caps], pale, 12,
                       axis_x=x - 0.3, squash=0.8)
        p.conform(core, lift=1.5)
        k.smooth(core, 50)


MODELS = {
    "pu_repulsor": (271, repulsor),
    "pu_pearl_wind": (273, pearl_wind),
    "pu_soul_of_zinglon": (275, soul_of_zinglon),
    "pu_attractor": (277, attractor),
    "pu_ice_beam": (121, ice_beam),
    "pu_flare": (123, flare),
    "pu_megalaser_dual": (3, megalaser_dual),
}
