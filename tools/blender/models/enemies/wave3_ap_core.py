"""Batch AP of wave 3 (sheet 3): the wreck of CORE's hooded figure (wave3_n.py), modelled as the sprites look
(models.cfg: yaw=0). The kit is wave3_ap_kit.py, the pixels wave3_ap_art.py (HOOD_DMG, in wave3_n_art.HOOD's frame).

Both pieces leave their wrecks in place when destroyed (enemies 251, 252 in CORE, dlevel -1): 3 237 -> 239,
275 -> 277. The stone head in the hood is smashed to jagged shards, the hood torn open round it, the cloak below
scorched.

- hooded_top_damaged, hooded_bottom_damaged (3 239, 277): wave3_n's whole figure (hooded_whole), its head replaced
  by broken stone where the damaged sprite draws it, cut as hooded_top and _bottom are (origin).

usage: Blender -b --factory-startup -P wave3_ap_core.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, w, Painter, Frame  # noqa: E402

orig = kit.load("wave3_n")
n = orig.n
kit.forget(n.MODELS, n.OBJECTS)

ORIGIN = orig.HOOD_ORIGIN
INTACT = Frame(orig.art.HOOD, 24, ORIGIN)
DAMAGED = kit.frame("HOOD_DMG", 24, ORIGIN)


def hooded_damaged():
    orig.hooded_whole()
    w.bake()
    f = DAMAGED
    dmg = kit.Damage(INTACT, DAMAGED)
    p = Painter("hood_dmg", shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10), 7: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)},
                metallic=0.05, roughness=0.6, finish={7: (0.0, 0.6)}, glow={0x77: 0.12, 0x78: 0.15, 0x79: 0.2})
    # The head smashed: the stone shards where the damaged sprite draws grey in the hood.
    kit.remove(["head"])
    kit.delete_over(kit.named("cloak"), dmg.gone, close=True, any_vertex=True)
    kit.remnant("shards", f, lambda c, r: (r <= 29 or ((c, r) in dmg.cells and r <= 40)) and f.get(c, r) is not None
                and f.get(c, r) >> 4 == 0 and (f.get(c, r) & 15) >= 3, 3.6, 4.2, p, edge=0.6, crumple=0.75, seed=1.0,
                walls=2)
    cloak = kit.named("cloak")
    kit.repaint(cloak, dmg, p, walls=2, blur=0, probe=0.3, soot=1, soot_radius=1.0, soot_chance=0.5)
    kit.sink(cloak, dmg, 1.0, min_z=0.4, seed=2.0)
    for obj in w.meshes():
        k.smooth(obj, 50)


def piece(name, sprite, top):
    y0, y1 = (0.0, 28.0) if top else (-28.0, 0.0)
    return (name, (-12.0, 12.0, y0, y1), (0.0, 14.0 if top else -14.0),
            lambda: DAMAGED.mask((0, 24, 0, 28) if top else (0, 24, 28, 56)))


n.pieced("hooded_damaged", hooded_damaged, (24, 56), [piece("hooded_top_damaged", 239, True),
                                                      piece("hooded_bottom_damaged", 277, False)])


if __name__ == "__main__":
    n.run()
