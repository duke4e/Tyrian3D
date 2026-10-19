"""Batch AP of wave 3 (sheet J): the damaged looks of TORM's and BONUS' grey machines on the foliage: the field gun's
barrel and the lens pad (wave3_m_ground.py), modelled as the sprites look (models.cfg:
yaw=0). The kit is wave3_ap_kit.py, the pixels wave3_ap_art.py (J1_DMG, J77_DMG, CANNON_DMG).

- field_gun_barrel_damaged (J 273; of J 89, enemy 764, dlevel -1: it stays so): wave3_m_ground's whole field gun
  (gun_whole), its barrel burnt and torn open along its top where the red lights were, its red tip blackened and
  broken, cut as field_gun_barrel is (origin); the breech and the mount (127, 129) keep their sprites.
- lens_pad_damaged (J 41; of J 77, enemy 749, dlevel 4): wave3_m_ground's lens pad, its green lens smashed (dark,
  splinters of green glowing in it), the pad burnt and dented (stand-alone, as lens_pad).

usage: Blender -b --factory-startup -P wave3_ap_torm.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole gun_damaged --preview <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, w, pal, Painter, Frame  # noqa: E402

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


# --- J 77 -> 41: the lens pad -----------------------------------------------------------------------------------------

@w.model("lens_pad_damaged", [(J, 41, True)])
def lens_pad_damaged():
    ground.lens_pad()
    w.bake()
    f = kit.frame("J77_DMG", 24, (12, 14))
    dmg = kit.Damage(Frame(ground.art.J77, 24, (12, 14)), f)
    p = painter("pad_dmg")
    # The lens smashed: its glossy dome flattened into dark glass, the bright core gone (the green splinters left
    # glow by the sprite's pixels).
    kit.remove(["lens_core"])
    glass = pal("pad_dmg_glass", 0x01, metallic=0.2, roughness=0.15)
    cx, cy = ground.px(10.6), ground.py(19.2)
    flat = (kit.Matrix.Translation((cx, cy, 3.8)) @ kit.Matrix.Diagonal((1.0, 1.0, 0.5, 1.0)) @
            kit.Matrix.Translation((-cx, -cy, -3.8)))
    for obj in kit.named("lens"):
        obj.data.materials.clear()
        obj.data.materials.append(glass)
        obj.data.transform(flat)
    kit.repaint(w.meshes(), dmg, p, walls=2, blur=0, soot=1, soot_radius=1.2, soot_chance=0.6)
    kit.sink([o for o in w.meshes() if o.name.startswith(("pad", "rim", "socket"))], dmg, 1.2, min_z=0.5, seed=6.0)
    kit.crack_lines("lens_crack", lambda x, y: 4.0 if (x - cx) ** 2 / 9.0 + (y - cy) ** 2 / 3.6 < 1.0 else None,
                    (cx + 0.4, cy - 0.2), pal("pad_dmg_crack", 0xcb, metallic=0.0, roughness=0.2, glow=0.9),
                    branches=5, length=3.0, step=0.5, radius=0.18, seed=7)
    for obj in w.meshes():
        k.smooth(obj, 50)
    kit.budget(4800)


if __name__ == "__main__":
    w.run()
