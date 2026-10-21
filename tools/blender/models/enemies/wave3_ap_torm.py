"""Batch AP of wave 3 (sheet J): the damaged looks of TORM's and BONUS' grey machines on the foliage: the field gun's
barrel (wave3_m_ground.py), modelled as the sprites look (models.cfg:
yaw=0). The kit is wave3_ap_kit.py, the pixels wave3_ap_art.py (J1_DMG, CANNON_DMG).

- field_gun_barrel_damaged (J 273; of J 89, enemy 764, dlevel -1: it stays so): wave3_m_ground's whole field gun
  (gun_whole), its barrel burnt and torn open along its top where the red lights were, its red tip blackened and
  broken, cut as field_gun_barrel is (origin); the breech and the mount (127, 129) keep their sprites.
(The lens pad damaged, J 41: polish_lens_pad.py.)

usage: Blender -b --factory-startup -P wave3_ap_torm.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole gun_damaged --preview <prefix>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, w, Painter, Frame  # noqa: E402

ground = kit.load("wave3_m_ground")
J = ground.J
kit.forget(w.MODELS, w.WHOLES)


def painter(prefix):
    return Painter(prefix, shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)}, metallic=0.3, roughness=0.55,
                   finish={7: (0.1, 0.4), 0xc: (0.1, 0.1)},
                   glow={0x73: 0.5, 0x74: 0.8, 0x75: 1.0, 0x76: 1.2, 0x77: 1.4, 0xc4: 0.6, 0xc5: 0.8, 0xc7: 1.0,
                         0xc9: 1.2})


# --- J 89 -> 273: the field gun's barrel ----------------------------------------------------------------------------

G_ORIGIN = ground.GUN_ORIGIN
G_INTACT = Frame(ground.art.CANNON, 72, G_ORIGIN)
G_DAMAGED = kit.frame("CANNON_DMG", 72, G_ORIGIN)


@w.whole("gun_damaged", (72, 56))
def gun_damaged():
    ground.gun_whole()
    w.bake()
    dmg = kit.Damage(G_INTACT, G_DAMAGED, keep=lambda c, r: r < 28)
    p = painter("gun_dmg")
    # The red lights torn out; the tip burnt and broken.
    kit.remove(["red_light"])
    B = ground.Vector((6.4, -2.6, 9.4))
    M = ground.Vector((-9.2, 13.4, 20.6))
    D = (M - B).normalized()
    for obj in kit.named("tip") + kit.named("bore"):
        kit.jag(obj, tuple(M + D * 0.6), tuple(D), 1.4, scale=0.7, seed=4.0)
    barrel = [o for o in w.meshes() if o.name.startswith(("barrel", "tip", "bore"))]
    kit.repaint(barrel, dmg, p, walls=1, blur=1, shift=-1.0, soot=2, soot_radius=1.6, soot_chance=0.7)
    kit.sink([o for o in barrel if o.name.startswith("barrel")], dmg, 1.8, min_z=6.0, seed=5.0)
    for obj in barrel:
        k.smooth(obj, 40)


def gun_piece(x0, x1, y0, y1):
    gun_damaged()
    w.bake()
    w.piece(w.meshes(), x0, x1, y0, y1)


w.model("field_gun_barrel_damaged", [(J, 273, True)])(lambda: gun_piece(-12, 12, 0, 28))


if __name__ == "__main__":
    w.run()
