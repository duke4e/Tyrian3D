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

The ground sprites drawn on rock and dirt (the purple pads and the eye block, the golden domes, the
golden pyramid, the red works) are in wave3_p_ground.py; the shared helpers in wave3_p_kit.py, the
pixel art in wave3_p_art.py.

usage: Blender -b --factory-startup -P wave3_p.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole rod --preview <prefix>]
"""
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_p_kit as w  # noqa: E402
from wave3_p_kit import pal, model, whole  # noqa: E402


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


w.run()
