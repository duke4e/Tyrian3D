"""Batch AP of wave 3 (sheet L): the damaged look of MINERS's tan dome creature (wave3_z_rock.py), modelled as the
sprites look (models.cfg: yaw=0). The kit is wave3_ap_kit.py, the pixels wave3_ap_art.py (TAN_DOME_DMG, in
wave3_z_art.DOME's frame).

Its top left piece leaves its wreck in its place when destroyed (enemy 1151: L 161 -> 238, dlevel -1): the glowing
nub on the head's top shot off, the head's crown chipped, burnt round the break.

- tan_dome_tl_damaged (L 238): wave3_z_rock's whole creature (dome_whole), damaged and cut as tan_dome_tl is
  (origin).

usage: Blender -b --factory-startup -P wave3_ap_miners.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, w, Painter  # noqa: E402

orig = kit.load("wave3_z_rock")
z = orig.kit
n = z.n
kit.forget(n.MODELS, n.OBJECTS)

DAMAGED = kit.frame("TAN_DOME_DMG", 48, (24, 28))


def dome_damaged():
    orig.dome_whole()
    w.bake()
    dmg = kit.Damage(orig.DOME, DAMAGED, keep=lambda c, r: c < 24 and r < 28)
    # The nub shot off with the left half of the head (the damaged sprite leaves it out): the body split down its
    # middle above the lower pieces, its left upper part gone, the break jagged; the left leg's shoulder with it.
    kit.remove(["nub"])
    cx = DAMAGED.X(24.0)
    body = kit.named("body")[0]
    upper = kit.split(body, (0.0, 1.6, 0.0), (0.0, 1.0, 0.0), "_upper")
    kit.cut_plane(upper, (cx + 0.3, 0.0, 0.0), (-1.0, 0.0, 0.0))
    kit.jag(upper, (cx + 0.3, 6.0, 8.0), (-1.0, 0.0, 0.0), 1.8, scale=0.9, seed=1.0)
    kit.jag(body, (cx - 4.0, 1.6, 6.0), (0.0, 1.0, 0.0), 1.2, scale=0.8, seed=2.0)
    for leg in kit.named("leg1"):
        kit.cut_plane(leg, (0.0, 2.2, 0.0), (0.0, 1.0, 0.0))
        kit.jag(leg, (-12.0, 2.2, 8.0), (0.0, 1.0, 0.0), 1.0, scale=0.7, seed=3.0)
    p = Painter("dome_dmg", shades={0xa: (2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13), 0: (1, 2, 3)}, metallic=0.1,
                roughness=0.55, glow={0x74: 0.4, 0x75: 0.5, 0x76: 0.7})
    kit.repaint(kit.named("body"), dmg, p, walls=2, blur=0, probe=0.3, soot=2, soot_radius=1.6, soot_chance=0.65)
    kit.sink(kit.named("body"), dmg, 1.2, min_z=1.0, seed=2.0)
    for obj in w.meshes():
        k.smooth(obj, 60)


z.pieced("tan_dome_damaged", dome_damaged, (48, 56), [z.quarter("tan_dome_tl_damaged", DAMAGED, 0, 0)])


if __name__ == "__main__":
    z.run()
