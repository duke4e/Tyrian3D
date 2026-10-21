"""Batch AP of wave 3 (sheet S): the damaged look of the asteroid levels' hangar (wave3_u_hangar.py), modelled as the
sprites look (models.cfg: yaw=0). The kit is wave3_ap_kit.py, the pixels wave3_ap_art.py (HANGAR_DMG). (The carrier's
launcher and robot damaged, S 273 and 237, are polish_carrier_turrets.py's; the eye turret's damaged look, S 275,
polish_eye_turret_dmg.py's.)

- roof_hangar_tl_damaged, roof_hangar_tr_damaged (S 17, 55; the dgr of 13 and 15, enemies 326, 327, dlevel -1: they
  stay so): wave3_u_hangar's whole hangar (hangar_whole) with its prow broken open, a black gash down the right
  slope beside the ridge with embers in it and a burnt hole in the left slope, cut as roof_hangar_tl and _tr
  (origin).

usage: Blender -b --factory-startup -P wave3_ap_ast.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole hangar_damaged --preview <prefix>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, w, Painter, Frame  # noqa: E402

hangar = kit.load("wave3_u_hangar")
u = hangar.u
kit.forget(w.MODELS, w.WHOLES)


def painter(prefix):
    return Painter(prefix, shades={0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)}, metallic=0.35, roughness=0.55,
                   finish={7: (0.2, 0.5), 4: (0.3, 0.45)}, glow={0x74: 0.5, 0x75: 0.6, 0x76: 0.8, 0x77: 1.0})


# --- The hangar -------------------------------------------------------------------------------------------------

H_INTACT = Frame(u.art.HANGAR, 48, hangar.ORIGIN)
H_DAMAGED = kit.frame("HANGAR_DMG", 48, hangar.ORIGIN)


@u.whole("hangar_damaged", (48, 84))
def hangar_damaged():
    hangar.hangar_whole()
    w.bake()
    dmg = kit.Damage(H_INTACT, H_DAMAGED, keep=lambda c, r: r < 28)
    p = painter("rh_dmg")
    parts = w.meshes()
    kit.repaint(parts, dmg, p, walls=2, blur=0, soot=2, soot_radius=1.5, soot_chance=0.7)
    # The gash and the hole: the roof pressed in deep where the sprite turns black, the ridge cap bent with it.
    kit.sink([o for o in parts if o.name.startswith(("hangar", "ridge", "eave"))], dmg, 3.2, min_z=1.0,
             along_normal=False, seed=1.0)
    for obj in w.meshes():
        k.smooth(obj, 30)
    return w.meshes()


def hangar_piece(cx, cy):
    objects = hangar_damaged()
    u.cut(objects, (cx - 12.0, cx + 12.0, cy - 14.0, cy + 14.0), (cx, cy))
    u.budget(4800)


u.model("roof_hangar_tl_damaged", [(17, True)])(lambda: hangar_piece(-12.0, 28.0))
u.model("roof_hangar_tr_damaged", [(55, True)])(lambda: hangar_piece(12.0, 28.0))


if __name__ == "__main__":
    u.run()
