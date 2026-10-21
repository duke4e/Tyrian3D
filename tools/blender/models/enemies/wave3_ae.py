"""Enemies of wave 3, batch AE (sheet ', written x27 in models.cfg): FRUIT's flying fruit, modelled as their
sprites look (models.cfg: yaw=0). The kit is wave3_ae_kit.py, the pixels wave3_ae_art.py; FRUIT's lemon beetle
and strawberry wing are in wave3_ae_lemon.py, CORAL's eel, worm and egg in wave3_ae_coral.py, FRUIT's pineapple
boss in wave3_ae_boss.py. Objects the levels put together from several sprites (the level files' enemy events
say how) are built whole and cut into their pieces, drawn at their own origins (origin). (The bladed orange, ' 78,
and the berry in the ring, ' 169: polish_orange_saw.py, polish_berry_ring.py.)

- grape_wing_l, grape_wing_r (' 130, 132; enemies 1227, 1228 at (x, y), (x + 24, y), in the sky or on the
  ground): a bunch of pale grapes round a glossy pod, two grapes hanging from curled stalks under it, on a dark
  purple wing with a spur at each tip. Built whole and cut in two (origin).

usage: Blender -b --factory-startup -P wave3_ae.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ae_kit as kit  # noqa: E402
from wave3_ae_kit import sh, w, pal, Painter  # noqa: E402


# --- ' 130 132: the grape wing ------------------------------------------------------------------------

GRAPES = kit.frame("GRAPES", 48, (24, 14))


def grape_spots(f):
    """The grapes the sprite draws (each a 4 x 4 ball with its highlight, index 0x5e, right of its middle):
    their centres (x, y), the pod's highlights in the middle left out."""
    out = []
    for r, row in enumerate(f.g):
        for c, val in enumerate(row):
            if val == 0x5e and not (21 <= c <= 26 and 9 <= r <= 15) and 3 <= c <= 44:
                out.append((c - f.ox, f.oy - (r + 1)))
    return out


def grape_wing_whole():
    f = GRAPES
    dark = Painter("gwing", shades={5: (0, 2, 3, 4, 5, 6, 8, 0xa, 0xb, 0xc)}, metallic=0.35, roughness=0.22)
    # The wing: a dark blade across the whole sprite, arched (its tips lower), thicker in the middle.
    wing_poly = [(-24.0, 0.2), (-20.5, 0.0), (20.5, 0.0), (24.0, 0.2), (24.0, 9.4), (22.8, 10.0), (-22.8, 10.0),
                 (-24.0, 9.4)]
    wing = kit.relief("gwing", [wing_poly], dark(0x54), sh.pillow_profile(1.4, 1.6, crown=0.5), bottom=0.7, base=5.0,
                      rim=0.4, spacing=0.5)
    kit.displace_z(wing, lambda x, y, z: -2.6 * (x / 24.0) ** 2)
    kit.paint_sprite(wing, f, dark, wall_steps=-2, keep=lambda val: val >> 4 == 5, default=dark(0x53), blur=1,
                     under=dark(0x50))
    # The spurs at its tips: pale spikes pointing down the screen.
    spur = pal("gwing_spur", 0x5c, metallic=0.4, roughness=0.3)
    for x in (-22.6, 22.6):
        kit.limb(f"gwing_spur{x:+.0f}", [(x, 10.4, 3.4), (x, 4.0, 3.0), (x, -1.5, 2.6), (x * 1.01, -6.0, 2.4)],
                 [0.9, 0.85, 0.6, 0.12], spur, segments=8)
    # The glossy pod in the middle of the bunch.
    pod_mats = Painter("gpod", shades={5: (5, 7, 0xa, 0xb, 0xc, 0xe), 7: (0xf,)}, metallic=0.2, roughness=0.15,
                       remap={0x7f: 0x5e})
    pod = w.sphere("gpod", (0.0, 3.4, 8.0), (3.9, 6.6, 4.8), pod_mats(0x57), 32, 18)
    for vt in pod.data.vertices:  # a teardrop, narrower towards its top
        vt.co.x *= 1.0 - 0.38 * kit.smoothstep(-1.0, 6.6, vt.co.y - 3.4)
    kit.paint_sprite(pod, f, pod_mats, wall_steps=-1, keep=lambda val: val >> 4 in (5, 7), default=pod_mats(0x55),
                     blur=1)
    glint = pal("gpod_glint", 0x7f, metallic=0.0, roughness=0.1, glow=0.6)
    at, nrm = kit.ellipsoid_point((0.0, 3.4, 8.0), (3.9, 6.6, 4.8), 0.0, 1.4)
    kit.lens("gpod_glint", at, nrm, (0.7, 0.9, 0.25), glint, sink=0.12, segments=12)
    # The grapes: a dome of pale berries round the pod, two curled strings of them hanging below.
    berries = [pal("grape_b", 0x5b, metallic=0.15, roughness=0.25), pal("grape_c", 0x5c, metallic=0.15, roughness=0.25)]
    stalk = pal("grape_stalk", 0x56, metallic=0.2, roughness=0.5)
    grapes = []
    for i, (x, y) in enumerate(grape_spots(f)):
        if y < -7.0:  # the hanging strings
            z = 4.2
        else:
            d = math.hypot(x / 12.0, (y - 3.0) / 11.0)
            z = 5.0 + 4.0 * max(0.0, 1.0 - d * d)
        grapes.append(w.sphere(f"grape{i}", (x, y, z), (2.5, 2.5, 2.3), berries[i % 2], 16, 8))
    # A few more behind them, filling the bunch out.
    for i, (x, y) in enumerate(((-3.0, 8.0), (3.0, 8.0), (-3.5, -2.5), (3.5, -2.5), (-7.5, 3.0), (7.5, 3.0))):
        grapes.append(w.sphere(f"grape_back{i}", (x, y, 4.6), (2.5, 2.5, 2.3), berries[(i + 1) % 2], 12, 6))
    kit.join(grapes, "grapes")
    # The stalks of the hanging strings: from the bunch's lowest grapes through theirs, hooking inwards.
    for side in (-1, 1):
        path = [(side * 4.5, -3.0, 6.0), (side * 6.5, -5.5, 5.2), (side * 7.0, -9.0, 4.2), (side * 4.0, -12.0, 4.2)]
        kit.limb(f"grape_stalk{side:+d}", path, [0.5] * len(path), stalk, segments=6)


kit.PROTECT += ["gpod"]
kit.pieced("grape_wing", grape_wing_whole, (48, 28), kit.grid_pieces("grape_wing_", GRAPES, ["l", "r"], 2, 1))


if __name__ == "__main__":
    kit.run()
