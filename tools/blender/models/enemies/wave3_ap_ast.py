"""Batch AP of wave 3 (sheet S): the damaged looks of the asteroid levels' hangar (wave3_u_hangar.py), the carrier's
launcher and robot (wave3_u_carrier.py) and the eye turret (misc.py), modelled as the sprites look (models.cfg:
yaw=0). The kit is wave3_ap_kit.py, the pixels wave3_ap_art.py (HANGAR_DMG, LAUNCHER_DMG, ROBOT_DMG, EYE, EYE_DMG).

- roof_hangar_tl_damaged, roof_hangar_tr_damaged (S 17, 55; the dgr of 13 and 15, enemies 326, 327, dlevel -1: they
  stay so): wave3_u_hangar's whole hangar (hangar_whole) with its prow broken open, a black gash down the right
  slope beside the ridge with embers in it and a burnt hole in the left slope, cut as roof_hangar_tl and _tr
  (origin).
- carrier_launcher_damaged (S 273; of 267, enemy 550): wave3_u_carrier's launcher, its pod burnt black round the
  red stripe and its tubes blown open (origin, raised onto the carrier's mount as carrier_launcher).
- carrier_robot_damaged (S 237; of 271, enemy 844): the robot, burnt and dented, its eyes out (origin).
- eye_turret_damaged (S 275; of 269, enemy 568, the most seen of these): misc.py's eye turret, its red dome cracked
  in dark seams, its grey lens burnt black, the ring round it scorched (stand-alone, as eye_turret).

usage: Blender -b --factory-startup -P wave3_ap_ast.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole hangar_damaged --preview <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, w, pal, Painter, Frame  # noqa: E402

hangar = kit.load("wave3_u_hangar")
carrier = kit.load("wave3_u_carrier")
misc = kit.load("misc", drop="all")
misc.export = lambda name: None  # its builders export as they go: here the build loop below does
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


# --- The launcher and the robot on the carrier -------------------------------------------------------------------

def small_damaged(build, intact_art, damaged_name, prefix, sink_depth=1.2, eyes=False):
    build()
    w.bake()
    dmg = kit.Damage(Frame(intact_art, 24, (12, 14)), kit.frame(damaged_name, 24, (12, 14)))
    p = painter(prefix)
    if eyes:  # the robot's eyes put out
        dark = pal(prefix + "_eye_out", 0x02, metallic=0.2, roughness=0.6)
        for obj in kit.named("eye"):
            obj.data.materials.clear()
            obj.data.materials.append(dark)
    kit.repaint(w.meshes(), dmg, p, walls=2, blur=0, soot=1, soot_radius=1.2, soot_chance=0.6)
    kit.sink(w.meshes(), dmg, sink_depth, min_z=-4.0, seed=2.0, min_nz=0.1)
    for obj in w.meshes():
        k.smooth(obj, 40)
    u.budget(4800)


u.model("carrier_launcher_damaged", [(273, True)])(
    lambda: small_damaged(carrier.launcher_parts, u.art.LAUNCHER, "LAUNCHER_DMG", "cl_dmg", 1.4))
u.model("carrier_robot_damaged", [(237, True)])(
    lambda: small_damaged(carrier.robot_parts, u.art.ROBOT, "ROBOT_DMG", "cr_dmg", 1.0, eyes=True))


# --- The eye turret ------------------------------------------------------------------------------------------------

@u.model("eye_turret_damaged", [(275, True)])
def eye_turret_damaged():
    misc.eye_turret()
    w.bake()
    dmg = kit.Damage(kit.frame("EYE", 24, (12, 14)), kit.frame("EYE_DMG", 24, (12, 14)), tolerance=2)
    p = painter("et_dmg")
    # The lens burnt black, the dome's glow turned down (embers in its cracks glow by the sprite).
    soot = pal("et_dmg_lens", 0x02, metallic=0.25, roughness=0.65)
    dome = pal("et_dmg_dome", 0x73, metallic=0.2, roughness=0.3, glow=0.3)
    for obj in w.meshes():
        if obj.name.startswith("lid"):
            obj.data.materials.clear()
            obj.data.materials.append(soot)
        elif obj.name.startswith("eye"):
            obj.data.materials.clear()
            obj.data.materials.append(dome)
    # The dome painted by the damaged sprite (its cracks dark, an ember glowing at its top left); the ring round it
    # (whose shapes the old model draws only roughly) scorched in patches.
    kit.repaint(kit.named("eye"), dmg, p, walls=2, blur=1)
    # Cracks across the dome from where it was hit (its top left, where the sprite's ember glows).
    def dome(x, y):
        t = 1.0 - ((x - 0.5) / 7.0) ** 2 - ((y - 1.5) / 7.0) ** 2
        return 3.6 + 4.2 * math.sqrt(t) if t > 0.04 else None
    kit.crack_lines("dome_crack", dome, (-2.6, 1.6), pal("et_dmg_crack", 0x01, metallic=0.2, roughness=0.7),
                    branches=7, length=8.0, radius=0.32, seed=5, ember=pal("et_dmg_ember", 0x76, metallic=0.1,
                                                                            roughness=0.3, glow=1.0))
    kit.cracks(kit.named("lid"), pal("et_dmg_split", 0x00, metallic=0.1, roughness=0.8), scale=1.6, width=0.12,
               depth=0.3, seed=2.0)
    base_p = Painter("et_dmg_base", metallic=0.5, roughness=0.5)
    for obj in kit.named("base"):
        kit.pixelate(obj, dmg.f1, step=4.0)
        kit.char([obj], base_p, amount=2, chance=0.55, seed=5.0)
    for obj in kit.named("lid"):
        kit.dent(obj, (0.5, 4.5), 2.6, 0.8, seed=4.0)
    for obj in w.meshes():
        k.smooth(obj, 50)
        if "stats" in k.args():
            print(f"   {obj.name}: {kit.triangles([obj])}")
    u.budget(4800)


if __name__ == "__main__":
    u.run()
