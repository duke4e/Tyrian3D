"""Batch AP of wave 3 (sheet G): the damaged look of the mortar of TORM, BONUS and BOTANY A (wave3_r.py), modelled as
the sprites look (models.cfg: yaw=0). The kit is wave3_ap_kit.py, the pixels wave3_ap_art.py (MORTAR_DMG).

The mortar's upper pieces switch to their damaged sprites when hit hard (enemy 768: G 165 -> 169, 769: G 167 -> 207;
dlevel -1, so they stay so): the barrel's plating torn open in dark burnt holes where the red lights were, the red
ring of its muzzle burnt black and its rim broken. The lower pieces (203, 205) keep their sprites.

- mortar_breech_damaged, mortar_muzzle_damaged (G 169, 207): wave3_r's whole mortar (mortar_whole), damaged, cut
  as mortar_breech and mortar_muzzle are (origin), so they swap in place and meet the intact lower pieces.

usage: Blender -b --factory-startup -P wave3_ap_mortar.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole mortar_damaged --preview <prefix>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import w, Frame, Painter  # noqa: E402

orig = kit.load("wave3_r")
r = orig.r
kit.forget(w.MODELS, w.WHOLES)

INTACT = Frame(r.art.MORTAR, 48, orig.MORTAR_ORIGIN)
DAMAGED = kit.frame("MORTAR_DMG", 48, orig.MORTAR_ORIGIN)


def mortar_damaged():
    """The whole mortar, its barrel torn and burnt where the damaged sprites show it (rows 13-27)."""
    orig.mortar_whole()
    w.bake()
    dmg = kit.Damage(INTACT, DAMAGED, keep=lambda c, row: row < 28)
    # The red lights along the barrel's top are gone: torn holes in their place.
    kit.remove(["light"])
    p = Painter("mortar_dmg", metallic=0.2, roughness=0.75, finish={7: (0.2, 0.6)})
    barrel = kit.named("barrel") + kit.named("band") + kit.named("muzzle") + kit.named("bore")
    # The muzzle's rim broken off unevenly, the bore with it.
    T = orig.Vector((orig.mpx(34.6), orig.mpy(16.4), 20.6))
    B = orig.Vector((orig.mpx(17.9), orig.mpy(31.4), 8.0))
    D = (T - B).normalized()
    for obj in kit.named("muzzle") + kit.named("bore"):
        kit.jag(obj, tuple(T + D * 0.2), tuple(D), 1.6, scale=0.8, seed=2.0)
    kit.repaint(barrel, dmg, p, walls=1, shift=-1.0, soot=3)
    kit.sink(kit.named("barrel") + kit.named("band"), dmg, 2.2, min_z=6.0, seed=1.0)
    # A dent where the plating is torn the most.
    for obj in kit.named("barrel"):
        kit.dent(obj, (orig.mpx(26.0), orig.mpy(23.0)), 3.0, 0.9, seed=3.0)
        orig.k.smooth(obj, 40)


r.whole("mortar_damaged", (48, 56))(mortar_damaged)


def piece(box, centre):
    mortar_damaged()
    w.bake()
    r.cut(w.meshes(), box, centre)
    r.stats_print(*w.meshes())
    r.budget(4800, floor=700)


r.model("mortar_breech_damaged", [(169, True)])(lambda: piece((-24, 0, 0, 28), (-12, 14)))
r.model("mortar_muzzle_damaged", [(207, True)])(lambda: piece((0, 24, 0, 28), (12, 14)))


if __name__ == "__main__":
    r.run()
