"""Enemies of wave 3, batch Z, continued (sheet L): MINERS's dark red rock, modelled as the sprites look (models.cfg:
yaw=0). The kit is wave3_z_kit.py, the pixels wave3_z_art.py.

MINERS's ground is red sand with patches of dark red rock laid with hexagonal cells (ramp 7, as the map draws
it); the level puts these objects of the same rock on it, all on the ground layer, all at the top of the screen
(y = -29) where the ground carries them down:

- red_mound_a_l, red_mound_a_r (L 234 beside 236, enemies 1144, 1145) and red_mound_b_l, red_mound_b_r (L 271
  beside 273, enemies 1146, 1147): low ridges of the rock along the sprites' bottom edge.
- tan_dome_tl, tan_dome_tr, tan_dome_bl, tan_dome_br (L 161 163 above 199 201, enemies 1151-1154): a tan
  creature standing on the ground: a fat body rising to a head up the screen with a red glowing nub on top, a
  thick leg on each side reaching out and down to the ground. The patch of rock the lower sprites draw round
  it is the map's ground (the 3D ground shows it): left out. The upper
  pieces' frames swell the nub into a fire ball (165/167, 203/205): the model keeps it glowing (glow).

Each object is built whole and cut into its sprites (origin).

usage: Blender -b --factory-startup -P wave3_z_rock.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_z_kit as kit  # noqa: E402
from wave3_z_kit import k, sh, w, pal, smoothstep  # noqa: E402

MOUND_A = kit.frame("MOUND_A", 48, (24, 14))
MOUND_B = kit.frame("MOUND_B", 48, (24, 14))
DOME = kit.frame("DOME", 48, (24, 28))


def rock_shade(f, ramps=(7, 0xf)):
    """The rock pixels' shades (the dull red ramp; the brown 0xf6 speckles as shade 3), blurred once."""
    value = lambda v: 3.0 if v >> 4 == 0xf else (v & 15) if v >> 4 == 7 else 2.0
    return kit.field_sampler(f, kit.field(f, value, lambda v: v >> 4 in ramps or v >> 4 == 4, blur=1))


def hex_rock(name, f, polys, height_of, edge, size=3.6, relief=0.45, seed=7):
    """A part of the hex rock over the polygons: its top at height_of(x, y, e) (e: 0 on the outline, 1 `edge`
    pixels in) with the cells bulging `relief` out of it, painted by the sprite's shades."""
    def z_of(x, y, e):
        bump, _ = kit.hex_cell(x, y, size)
        return height_of(x, y, e) + relief * (bump - 0.5) * min(1.0, 2.0 * e)
    obj = kit.heightfield(name, polys, z_of, None, spacing=0.45, smooth_angle=40, edge=edge)
    kit.hex_rock_paint(obj, rock_shade(f), kit.lava_rock_mats("hexrock"), size=size, seed=seed)
    return obj


def halves(name, f):
    return [kit.quarter(name + "_l", f, 0, 0), kit.quarter(name + "_r", f, 24, 0)]


# --- L 234 236 and L 271 273: the mounds -----------------------------------------------------------

def mound(name, f, seed):
    polys = kit.polys_of(f, lambda v, c, r: True, smooth=2, epsilon=0.3)
    hex_rock(name, f, polys, lambda x, y, e: 0.3 + 5.6 * e, edge=3.4, size=3.4, relief=0.5, seed=seed)


kit.pieced("red_mound_a", lambda: mound("mound_a", MOUND_A, 11), (48, 28), halves("red_mound_a", MOUND_A))
kit.pieced("red_mound_b", lambda: mound("mound_b", MOUND_B, 23), (48, 28), halves("red_mound_b", MOUND_B))


# --- L 161 163 / 199 201: the tan dome creature in its rock ----------------------------------------

# The body's half-width in each row (from the sprite: its outline, between the dark gaps beside the legs) and
# its height there; the body is symmetric about the middle of column 24.
BODY = [(17, 1.4, 12.2), (18, 2.4, 13.6), (19, 3.8, 14.6), (20, 4.6, 15.2), (21, 5.5, 15.6), (22, 6.4, 15.8),
        (23, 7.3, 15.9), (25, 8.4, 15.7), (27, 9.2, 15.2), (30, 9.6, 14.4), (34, 9.6, 13.2), (38, 9.5, 11.6),
        (42, 9.2, 9.6), (44, 8.8, 8.2), (46, 7.4, 6.0), (47.6, 4.2, 3.6), (48.3, 1.0, 1.5)]


def dome_whole():
    f = DOME
    X, Y = f.X, f.Y
    cx = X(24.0)
    tan_field = kit.field(f, lambda v: v & 15, lambda v: v >> 4 == 0xa, blur=2)
    tan_at = kit.field_sampler(f, tan_field)
    tans = kit.bands("dome_tan", 0xa, (4, 5, 6, 7, 8, 9, 10, 11, 12, 13), metallic=0.1, roughness=0.5)

    # The body: lofted along the screen from its tail (row 48) to its head (row 17), flat underneath.
    rings = []
    for row, hw, h in reversed(k.profile(BODY, 0.5)):
        rings.append(k.ring(Y(row), max(hw, 0.3), max(h, 0.5), 48, z=0.0, x=cx, top=1.0, bottom=0.02, power=2.2))
    body = k.loft("body", rings, tans[4][1], start_point=(cx, Y(48.6), 0.4), end_point=(cx, Y(16.6), 10.5))
    k.smooth(body, 60)
    kit.paint_by(body, lambda x, y: tan_at(x, y) + 0.4, tans, wall_drop=1.2)
    # The red nub on the head's top, glowing.
    nub = pal("dome_nub", 0x77, metallic=0.0, roughness=0.4, glow=1.2)
    nub_hot = pal("dome_nub_hot", 0x7b, metallic=0.0, roughness=0.4, glow=2.0)
    w.sphere("nub", (cx, Y(18.2), 13.9), (1.9, 1.7, 1.5), nub, 16, 8)
    w.sphere("nub_hot", (cx - 0.3, Y(18.0), 15.0), (0.9, 0.8, 0.6), nub_hot, 10, 5)

    # The legs: from the shoulders out and down the screen to the ground (columns 4-15 and their mirror).
    leg_lit, leg = tans[6][1], tans[3][1]
    for side in (-1, 1):
        def P(col, row, z):
            return Vector((cx + side * (X(col) - cx), Y(row), z))
        path = w.catmull([P(17.0, 25.5, 10.5), P(11.5, 26.8, 10.0), P(7.6, 29.5, 8.2), P(6.6, 35.0, 5.6),
                          P(6.6, 41.0, 2.6), P(7.0, 45.0, 0.2)], 0.5)
        radii = [3.3 - 0.4 * smoothstep(0.0, 0.35, i / len(path)) - 0.5 * smoothstep(0.6, 1.0, i / len(path))
                 for i in range(len(path))]
        limb = w.tube(f"leg{side}", path, radii, leg_lit, 18)
        kit.paint_by(limb, lambda x, y: tan_at(x, y) + 0.4, tans, wall_drop=1.6)
        # The knuckle where it meets the ground.
        w.sphere(f"foot{side}", tuple(P(7.0, 44.6, 0.8)), (2.6, 2.0, 1.2), leg, 14, 7)
    sh.flat_bottom(w.meshes(), 0.0)


kit.pieced("tan_dome", dome_whole, (48, 56), [kit.quarter("tan_dome_tl", DOME, 0, 0),
                                              kit.quarter("tan_dome_tr", DOME, 24, 0),
                                              kit.quarter("tan_dome_bl", DOME, 0, 28),
                                              kit.quarter("tan_dome_br", DOME, 24, 28)])


if __name__ == "__main__":
    kit.run()
