"""Enemies of wave 3, batch W, continued (sheet P: the asteroid levels): ASTEROID?'s tan launcher, modelled as
its sprite looks (models.cfg: yaw=0); the kit is wave3_w_kit.py, the pixels wave3_w_art.py.

- tan_launcher (P 277): a tan housing standing on the ground, arched over two stubby barrels that point
  down the screen and up, each in a blue-grey breech, a tan sleeve and a tan muzzle round a red glowing
  bore; a dark blue window in the housing's top, a blue-grey cowl at its back and red fins at its sides.
  The frames push the barrels out (275, 273, 271) and then hide it (0): the model shows them in. The
  asteroid floor the sprite draws round it is the map's ground (the game draws it under it): not modelled
  (batch AV); the housing, the fins and the barrels' feet stand on the ground (z 0).

usage: Blender -b --factory-startup -P wave3_w_launcher.py -- [--preview <prefix>] [--check 1] [--stats 1]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_w_kit as kit  # noqa: E402
from wave3_w_kit import art, k, sh, w, p, pal  # noqa: E402

LAUNCHER = kit.Frame(art.LAUNCHER, 24, (12, 14))


@kit.model("tan_launcher", mask=lambda: LAUNCHER.mask())
def tan_launcher():
    f = LAUNCHER
    X, Y = f.X, f.Y
    tan = pal("tl_tan", 0xa9, metallic=0.45, roughness=0.4)
    tan_lit = pal("tl_tan_lit", 0xab, metallic=0.45, roughness=0.35)
    tan_dark = pal("tl_tan_dark", 0xa6, metallic=0.4, roughness=0.45)
    blue = pal("tl_blue", 0x67, metallic=0.55, roughness=0.35)
    blue_dark = pal("tl_blue_dark", 0x64, metallic=0.5, roughness=0.4)
    glass = pal("tl_glass", 0x63, metallic=0.4, roughness=0.08)
    glint = pal("tl_glint", 0x6c, metallic=0.2, roughness=0.1, glow=0.5)
    red = pal("tl_red", 0x74, metallic=0.3, roughness=0.4)
    bore = pal("tl_bore", 0x74, metallic=0.0, roughness=0.5, glow=0.7)

    # No floor under it: the sprite's floor is the map's ground, which the game draws under it (batch AV).

    # The housing: an arched block over the breeches (rows 0-11, columns 2-20).
    house = w.block("housing", (X(11.0), Y(6.0)), 9.4, 5.8, 7.2, tan, taper=0.8, rounding=2.6, power=3.0,
                    segments=32, z0=0.0, dome=1.2)
    kit.paint_faces(house, lambda c, nrm: tan if nrm.z > 0.85 else tan_lit if (nrm.z > 0.2 and (nrm.x < -0.3 or
                                                                                              nrm.y > 0.3)) else
                    tan_dark)
    # The cowl at its back, the window in its top and the red fins at its sides.
    kit.rounded_box("cowl", (X(11.5), Y(1.2), 6.2), (11.0, 2.6, 3.0), blue, bevel=0.8)
    kit.rounded_box("window", (X(11.0), Y(7.6), 7.7), (5.6, 2.6, 0.9), glass, bevel=0.35)
    w.sphere("window_glint", (X(10.2), Y(7.2), 8.15), (1.2, 0.5, 0.2), glint, 8, 4)
    # The raised T on its top.
    kit.rounded_box("t_bar", (X(11.0), Y(3.4), 7.9), (13.0, 2.4, 1.0), tan_lit, bevel=0.4)
    kit.rounded_box("t_stem", (X(11.0), Y(5.2), 8.0), (3.2, 2.6, 1.0), tan_lit, bevel=0.4)
    for name, c0, c1 in (("fin_l", 1, 2), ("fin_r", 20, 22)):
        kit.prism_x(name, [(f.top(7), 0.0), (f.top(7), 6.0), (f.bottom(9), 6.4), (f.bottom(11), 0.0)],
                    f.left(c0) + 0.3, f.right(c1) - 0.3, red, bevel=0.3)

    # The barrels: down the screen and up from the housing's front, the red bore glowing in each muzzle.
    elevation = math.radians(40.0)
    d = Vector((0.0, -math.cos(elevation), math.sin(elevation)))
    for name, c in (("l", 4.5), ("r", 17.5)):
        start = Vector((X(c), Y(9.5), 3.2))
        breech = w.lathe_axis(f"breech_{name}", [(0.0, 2.4), (0.4, 2.8), (3.4, 2.8), (3.8, 2.5)], blue, tuple(start),
                              tuple(d), 16)
        kit.paint_faces(breech, lambda c_, nrm: blue_dark if nrm.z < 0.2 else None)
        w.lathe_axis(f"ring_{name}", [(3.6, 2.6), (3.8, 3.2), (4.6, 3.2), (4.8, 2.7)], blue_dark, tuple(start),
                     tuple(d), 16)
        sleeve = w.lathe_axis(f"sleeve_{name}", [(4.6, 2.9), (4.9, 3.3), (8.0, 3.4), (8.6, 3.7), (10.4, 3.8),
                                                (10.9, 3.4), (11.1, 2.2), (10.7, 1.9), (10.5, 0.01)], tan, tuple(start),
                              tuple(d), 20)
        kit.paint_faces(sleeve, lambda c_, nrm: tan_dark if nrm.z < 0.1 else tan_lit if nrm.y > 0.4 else None)
        mouth = start + d * 10.55
        w.lathe_axis(f"bore_{name}", [(0.0, 1.85), (0.3, 1.85), (0.32, 0.01)], bore, tuple(mouth), tuple(d), 14)
        # The barrel's foot on the ground.
        kit.rounded_box(f"foot_{name}", (X(c), Y(12.5), 0.85), (6.0, 4.0, 1.7), blue_dark, bevel=0.5)


kit.run()
