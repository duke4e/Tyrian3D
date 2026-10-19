"""Wave 3, batch P of the enemy models: the remaining enemies of sheet 2 (episode 1: TYRIAN, HOLES, TYRIAN X,
and SAVARA, ASSASSIN, BONUS, GYGES, EYESPY), modelled as their sprites look (models.cfg: yaw=0). Objects the
game draws from several sprites are built whole and cut into the sprites' pieces (models.cfg: origin);
the level files' enemy events say how the pieces are placed. (The walker, 2 85 beside 2 87, is built by
polish_walker.py.)

- rod_butt, rod_segment, rod_tip (2 1, 2 3, 2 5) and their mirror images rod_tip_l, rod_segment_l,
  rod_butt_r (2 7, 2 9, 2 11): the long grey rods of TYRIAN that push in from the screen's sides,
  red collars and bands round them and a polished tip: the events lay a butt, a row of segments (the
  levels repeat 3 and 9 every 24 pixels) and a tip side by side, so the segments' ends are the plain
  rod and meet (origin).
- hood_turret (2 153): the hooded turret sunk in the rocks of TYRIAN: a dark pyramid hood over a red
  band with a red eye that glows (its frames brighten the eye), red claws below it, grey boulders and
  tan stones round it (origin, as TYRIAN's purple pads near it).

The ground sprites drawn on rock and dirt (the purple pads and the eye block, the golden domes, the
golden pyramid, the red works) are in wave3_p_ground.py; the shared helpers in wave3_p_kit.py, the
pixel art in wave3_p_art.py.

usage: Blender -b --factory-startup -P wave3_p.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole rod --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_p_kit as w  # noqa: E402
from wave3_p_kit import art, k, sh, pal, model, whole, grid, ramp, shade  # noqa: E402


# --- 2 1, 3, 5 and their mirror images 2 7, 9, 11: the rods (72 x 28 whole) ----------------------------
# The whole rod runs along x from -36 (its butt, sprite 1) to 36 (the tip's end, sprite 5); sprite 3 is
# x -12..12, which the levels repeat: its ends are the plain rod, so the copies meet. t = x + 36.

ROD_Z = 8.0  # the axis's height: the big collars rest on the ground
ROD_Y = 1.0  # the axis's y (rows 7-18 of the sprites)


def rod_whole():
    steel = pal("rod_steel", 0x08, metallic=0.65, roughness=0.3)
    tip_mat = pal("rod_tip", 0x0b, metallic=0.8, roughness=0.18)
    dark = pal("rod_dark", 0x02, metallic=0.5, roughness=0.5)
    red = pal("rod_red", 0x48, metallic=0.4, roughness=0.3)
    red_light = pal("rod_red_light", 0x4b, metallic=0.4, roughness=0.26)
    brown = pal("rod_brown", 0x12, metallic=0.3, roughness=0.5)
    necks = [(11.0, 14.0), (36.0, 39.0), (44.0, 47.0)]
    collars = [(18.2, 23.8, 8.0), (27.0, 31.0, 7.0)]
    r0 = 6.0
    # The rod: a rounded butt, necks where the red bands sit, the long tip.
    prof = [(0.0, 0.0), (0.15, 3.4), (0.6, 5.0), (1.4, 5.8), (2.4, r0)]
    for a, b in necks:
        prof += [(a - 0.6, r0), (a, 5.4), (a + 0.6, 4.3), (b - 0.6, 4.3), (b, 5.4), (b + 0.6, r0)]
    prof += [(48.0, r0), (51.0, 5.85), (54.0, 5.5), (57.0, 4.9), (60.0, 4.1), (63.0, 3.0), (66.0, 1.8), (68.0, 0.7),
             (68.6, 0.0)]
    rod = w.lathe_axis("rod", prof, steel, (-36.0, ROD_Y, ROD_Z),
                       (1, 0, 0), 28, smooth_angle=40)
    # The tip is polished; a dark seam where it starts.
    w.paint_faces(rod, lambda c, n: tip_mat if c.x > 12.6 else None)
    w.lathe_axis("tip_seam", [(0.0, 6.05), (0.5, 6.15), (1.0, 6.05)], dark, (12.0, ROD_Y, ROD_Z), (1, 0, 0), 28)
    # The butt's dark cap.
    w.lathe_axis("butt_cap", [(0.0, 0.0), (0.05, 2.6), (0.35, 3.3), (0.6, 3.6)], dark, (-36.05, ROD_Y, ROD_Z), (1, 0, 0),
                 20)
    # Red bands round the necks.
    for i, (a, b) in enumerate(necks):
        band = w.lathe_axis(f"band{i}", [(0.0, 4.2), (0.3, 4.75), (b - a - 1.0 - 0.3, 4.75), (b - a - 1.0, 4.2)], red,
                            (-36.0 + a + 0.5, ROD_Y, ROD_Z), (1, 0, 0), 24)
        w.paint_faces(band, lambda c, n: red_light if n.z > 0.55 and n.x <= 0.2 else None)
    # The red collars, a dark lip either side; the big one sits on a brown clamp.
    for i, (a, b, rc) in enumerate(collars):
        x0 = -36.0 + a
        coll = w.lathe_axis(f"collar{i}", [(0.0, r0 - 0.2), (0.25, rc - 0.6), (0.6, rc), (b - a - 0.6, rc),
                                          (b - a - 0.25, rc - 0.6), (b - a, r0 - 0.2)], red, (x0, ROD_Y, ROD_Z),
                            (1, 0, 0), 28, smooth_angle=35)
        w.paint_faces(coll, lambda c, n: red_light if n.z > 0.6 else None)
        for x in (x0 + 0.15, x0 + (b - a) - 0.15):
            w.lathe_axis(f"collar_lip{i}_{x:.0f}", [(0.0, rc - 0.4), (0.3, rc + 0.15), (0.6, rc - 0.4)], dark,
                         (x - 0.3, ROD_Y, ROD_Z), (1, 0, 0), 28)
        foot_h = ROD_Z - rc + 1.2
        w.rounded_box(f"clamp{i}", (x0 + (b - a) / 2, ROD_Y - 0.5, foot_h / 2), (b - a - 0.6, 6.0, foot_h), brown,
                      bevel=0.4)


@whole("rod", (72, 28))
def rod_preview():
    rod_whole()


def rod_piece(x0, mirror):
    rod_whole()
    w.bake()
    w.piece(w.meshes(), x0, x0 + 24, -14, 14)
    if mirror:
        w.mirror_all()


@model("rod_butt", [1])
def rod_butt():
    rod_piece(-36, False)


@model("rod_segment", [3])
def rod_segment():
    rod_piece(-12, False)


@model("rod_tip", [5])
def rod_tip():
    rod_piece(12, False)


@model("rod_tip_l", [7])
def rod_tip_l():
    rod_piece(12, True)


@model("rod_segment_l", [9])
def rod_segment_l():
    rod_piece(-12, True)


@model("rod_butt_r", [11])
def rod_butt_r():
    rod_piece(-36, True)


# --- 2 153: the hooded turret in the rocks --------------------------------------------------------------

def P(col, row):
    """A pixel corner (column, row) of a 24 x 28 sprite as (x, y)."""
    return (col - 12.0, 14.0 - row)


@model("hood_turret", [153])
def hood_turret():
    """A dark pyramid hood pointing up the screen, its ridge catching the light, sunk in grey rocks
    with tan stones; its front slopes down to a red band with a glowing red eye in the middle, a dark
    jaw below and two red claws curling down either side."""
    g = grid(art.TURRET, 24)
    hood_mat = pal("hood_grey", 0x04, metallic=0.55, roughness=0.35)
    hood_light = pal("hood_light", 0x08, metallic=0.55, roughness=0.3)
    ridge_mat = pal("hood_ridge", 0x0c, metallic=0.6, roughness=0.25)
    band = pal("hood_band", 0x46, metallic=0.4, roughness=0.3)
    band_light = pal("hood_band_light", 0x49, metallic=0.4, roughness=0.28)
    jaw = pal("hood_jaw", 0x02, metallic=0.5, roughness=0.4)
    claw = pal("hood_claw", 0x45, metallic=0.4, roughness=0.32)
    claw_light = pal("hood_claw_light", 0x48, metallic=0.4, roughness=0.3)
    eye = pal("hood_eye", 0x79, metallic=0.0, roughness=0.15, glow=1.8)
    eye_hot = pal("hood_eye_hot", 0x7c, metallic=0.0, roughness=0.1, glow=3.0)
    socket = pal("hood_socket", 0x41, metallic=0.3, roughness=0.4)

    # The rocks round it, low under the hood.
    def is_rock(v, c, r):
        if v is None:
            return False
        x, y = c + 0.5 - 12, 14 - r - 0.5
        inside_hood = y < 11.8 and y > -4.0 and abs(x + 0.3) < 0.4 + (11.8 - y) * 0.95 and abs(x + 0.3) < 9.0
        return ramp(v) in (0, 0xa) and not inside_hood and not (r >= 17 and ramp(v) == 4)
    w.grey_rocks("rocks", g, is_rock, prefix="hood", keep_base=lambda v, c, r: v is not None)

    # The hood: diamond sections along y, its ridge highest just behind the band.
    sections = [(11.9, 0.3, 0.6), (10.5, 1.4, 2.2), (8.5, 3.0, 3.9), (6.5, 4.6, 5.4), (4.5, 6.3, 6.9), (2.8, 7.8, 8.0),
                (1.8, 8.5, 8.2), (0.6, 8.8, 7.4), (-0.8, 8.7, 5.9), (-2.2, 8.0, 4.0), (-3.2, 6.6, 2.0), (-3.7, 5.0, 0.6)]
    rings = [k.ring(y, hw, 1.0, 24, z=0.3, x=-0.3, top=top, bottom=0.3, power=1.25) for y, hw, top in sections]
    split = 6  # the section at y = 1.8: the band starts there
    hood = k.loft("hood", rings[:split + 1], hood_mat, start_point=(-0.3, 12.2, 0.4), end_point=(-0.3, 1.0, 1.0))
    k.smooth(hood, 28)
    w.paint_faces(hood, lambda c, n: hood_light if n.x < -0.25 and n.z > 0.3 else None)
    front = k.loft("band", rings[split:], band, start_point=(-0.3, 2.6, 1.0), end_point=(-0.3, -3.9, 0.4))
    k.smooth(front, 28)
    w.paint_faces(front, lambda c, n: band_light if n.z > 0.7 else None)
    # The ridge: a bright edge along the top from the point to the band.
    ridge = [(-0.3, 11.6, 1.05), (-0.3, 8.5, 4.35), (-0.3, 4.5, 7.35), (-0.3, 2.4, 8.55)]
    w.tube("ridge", w.catmull(ridge, 0.5), 0.42, ridge_mat, 6)
    # The eye in the band's middle: a dark socket and the glowing lens.
    ex, ey, ez = -0.3, -0.2, 6.1
    w.sphere("socket", (ex, ey, ez - 0.4), (3.4, 2.4, 1.6), socket, 18, 8)
    w.sphere("eye", (ex, ey - 0.2, ez + 0.1), (2.6, 1.9, 1.5), eye, 18, 9)
    w.sphere("eye_hot", (ex - 0.4, ey + 0.1, ez + 1.2), (1.1, 0.8, 0.5), eye_hot, 10, 5)
    # The dark jaw under the band.
    w.block("jaw", (-0.3, -4.7), 3.0, 1.6, 1.8, jaw, rounding=0.6, power=3.0, segments=20)
    # The red claws curling down either side, thinning to their tips.
    for side, pts in ((-1, [(7.5, 16.8, 3.0), (5.2, 20.0, 2.6), (4.3, 23.0, 2.0), (5.4, 25.2, 1.5), (7.2, 25.6, 1.2)]),
                      (1, [(15.5, 16.8, 3.0), (17.8, 20.0, 2.6), (18.7, 23.0, 2.0), (17.6, 25.2, 1.5),
                           (15.8, 25.6, 1.2)])):
        path = w.catmull([(c - 12.0, 14.0 - r, z) for c, r, z in pts], 0.5)
        n = len(path)
        radii = [1.7 * (1.0 - 0.6 * (i / (n - 1)) ** 1.5) for i in range(n)]
        cl = w.tube(f"claw{side}", path, radii, claw, 10)
        w.paint_faces(cl, lambda c, nn: claw_light if nn.z > 0.6 else None)


w.run()
