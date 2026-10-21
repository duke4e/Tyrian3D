"""Enemies of wave 3, batch Z, continued (sheet L): the small creatures of SQUADRON and TIME WAR and two of MINERS's
flyers, modelled as their sprites look (models.cfg: yaw=0). The kit is wave3_z_kit.py, the pixels wave3_z_art.py.
(The spiked fire ball, L 116, and the eyeball, L 117: polish_fire_spike_ball.py, polish_squad_eyeball.py.)

- red_mouth_lander (L 229): MINERS's grey lander (in the sky; one stands in SQUADRON): an armoured shell with
  a slatted face over a red mouth, a red glowing jet under it and two legs reaching down the screen.
(MINERS's fighter, L 267: polish_pod_fighter.py.)

usage: Blender -b --factory-startup -P wave3_z_small.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1]
"""
import os
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_z_kit as kit  # noqa: E402
from wave3_z_kit import sh, w, pal, smoothstep  # noqa: E402

MECH = kit.frame("MECH", 24, (12, 14))


# --- L 229: the lander -----------------------------------------------------------------------------

@kit.model("red_mouth_lander", mask=lambda: MECH.mask())
def red_mouth_lander():
    f = MECH
    X, Y = f.X, f.Y
    paint = kit.Painter("lander", shades={0: (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)}, metallic=0.35, roughness=0.35,
                        remap={0x01: 0x03, 0x02: 0x03})
    dark = pal("lander_dark", 0x02, metallic=0.4, roughness=0.5)
    slat = pal("lander_slat", 0x0b, metallic=0.6, roughness=0.3)
    red = pal("lander_red", 0x74, metallic=0.2, roughness=0.35, glow=0.4)
    jet = pal("lander_jet", 0x79, metallic=0.0, roughness=0.4, glow=1.4)
    jet_hot = pal("lander_jet_hot", 0x7c, metallic=0.0, roughness=0.4, glow=2.2)
    leg = pal("lander_leg", 0x07, metallic=0.6, roughness=0.3)
    leg_lit = pal("lander_leg_lit", 0x0b, metallic=0.6, roughness=0.3)
    # The shell: rows 1-17, a dome highest towards its back (up the screen), its face sloping down to the
    # mouth; painted by the sprite (its seams and panels).
    shell_f = kit.frame("MECH", 24, (12, 14)).fill({0x01, 0x02}, edge_only=True)
    polys = kit.polys_of(f, lambda v, c, r: r <= 17 and not (r >= 13 and 9 <= c <= 15 and v >> 4 == 7), smooth=2,
                         epsilon=0.3)
    yc = Y(6.5)

    def shell_z(x, y, e):
        back = smoothstep(Y(17.5), Y(5.0), y)
        return 3.2 + e * (5.5 + 4.0 * back) - 0.02 * x * x * (1 - back)
    shell = kit.heightfield("shell", polys, shell_z, None, spacing=0.5, smooth_angle=45, edge=4.5)
    kit.pixelate(shell, shell_f)
    kit.paint_sprite(shell, shell_f, paint, wall_steps=2, under=dark, blur=1)
    kit.merge_flat(shell)
    shell.data.validate()
    # The face's slats (rows 9-14, columns 9-15: light and dark stripes) as raised bars.
    for c in (9.5, 11.5, 13.5):
        kit.rounded_box(f"slat{c}", (X(c) + 0.5, Y(11.0), 9.4), (0.9, 6.0, 1.0), slat, bevel=0.3)
    # The mouth: a red glowing hollow under the face (rows 13-15), its lip a dark ridge.
    w.sphere("mouth", (X(12.0), Y(14.0), 4.6), (3.8, 1.8, 1.6), red, 18, 9)
    # The jet under the body (rows 16-24): a dark cowl down the screen with a red cone in it, pointing down
    # the screen and glowing at its end.
    kit.rounded_box("jet_cowl", (X(12.0), Y(19.6), 1.9), (6.6, 8.0, 3.4), leg, bevel=1.2)
    w.lathe_axis("jet", [(0.0, 2.4), (2.4, 2.4), (3.8, 2.0), (4.8, 1.3), (5.3, 0.01)], jet, (X(12.0), Y(17.0), 4.0),
                 (0, -1, 0.1), 18)
    w.sphere("jet_core", (X(12.0), Y(21.6), 4.4), (1.2, 1.1, 1.0), jet_hot, 12, 6)
    # The legs: from under the shell's lower corners down the screen to feet at the sprite's bottom
    # corners (columns 0-5 and 18-23, rows 17-27), bent at the knee.
    for side, (hip_c, knee_c, foot_c) in (("l", (4.5, 3.0, 1.6)), ("r", (19.5, 21.0, 22.4))):
        hip = Vector((X(hip_c), Y(15.5), 5.0))
        knee = Vector((X(knee_c), Y(20.0), 6.2))
        foot = Vector((X(foot_c), Y(25.6), 1.0))
        w.tube(f"thigh_{side}", w.catmull([hip, knee], 0.5), 1.7, leg_lit, 14)
        w.tube(f"shin_{side}", w.catmull([knee, (knee + foot) / 2 + Vector((0, 0.3, 0.5)), foot], 0.5), 1.45, leg, 14)
        w.sphere(f"knee_{side}", tuple(knee), (2.0, 2.0, 1.8), leg_lit, 16, 8)
        w.sphere(f"foot_{side}", tuple(foot + Vector((0, -0.4, -0.1))), (2.1, 1.8, 1.1), dark, 14, 7)
    sh.flat_bottom(w.meshes(), 0.0)


if __name__ == "__main__":
    kit.run()
