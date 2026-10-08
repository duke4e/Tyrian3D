"""Batch AP of wave 3 (sheet H): the damaged look of the glossy cap of GYGES' grey stalk (wave3_ad_wall.py),
modelled as the sprites look (models.cfg: yaw=0). The kit is wave3_ap_kit.py, the pixels wave3_ap_art.py
(PURPLE_DMG, in wave3_ad_art.PURPLE's frame).

The cap leaves its wreck in its place when destroyed (enemy 416: H 79 -> 41, dlevel -1): its glossy shell burst open,
two jagged halves of it standing at its sides round a crater of dark, torn flesh with red glowing in its depths.

- gyges_stalk_cap_damaged (H 41): wave3_ad_wall's whole stalk (stalk_whole), its cap burst, cut as gyges_stalk_cap
  is (origin).

usage: Blender -b --factory-startup -P wave3_ap_gyges.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, w  # noqa: E402

orig = kit.load("wave3_ad_wall")
ad = orig.kit
n = ad.n
kit.forget(n.MODELS, n.OBJECTS)

DAMAGED = ad.Frame(kit.art.PURPLE_DMG, 48, (24, 56))


def stalk_damaged():
    orig.stalk_whole()
    w.bake()
    dmg = kit.Damage(orig.STALK, DAMAGED, keep=lambda c, r: r < 28)
    p = ad.Painter("stalk_dmg", shades={6: (2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf), 0: (1, 2, 3, 4),
                                        7: (1, 2, 3, 4, 5, 6, 7)},
                   metallic=0.1, roughness=0.3, glow={0x73: 0.5, 0x74: 0.7, 0x75: 0.9, 0x76: 1.1, 0x77: 1.3})
    cap = kit.named("stalk_cap")
    kit.delete_over(cap, dmg.gone, close=True, any_vertex=True)
    cap = kit.named("stalk_cap")
    # The crater: the shell pressed deep where the sprite turns dark or red (the burst), its halves left standing.
    kit.repaint(cap, dmg, p, walls=2, blur=0, probe=0.3)
    kit.sink(cap, dmg, 6.0, min_z=9.0, along_normal=False, power=0.5, noisy=0.3, seed=1.0)
    # Slivers of the shell left standing over nothing the sprite draws: gone.
    kit.delete_over(cap, lambda x, y: DAMAGED.at(x, y) is None and y > DAMAGED.Y(27.0) and
                    DAMAGED.at(x, y - 1.0) is None)
    for obj in w.meshes():
        k.smooth(obj, 50)


ad.pieced("gyges_stalk_damaged", stalk_damaged, (48, 84),
          [ad.piece("gyges_stalk_cap_damaged", DAMAGED, 12, 0)])


if __name__ == "__main__":
    ad.run()
