"""Batch AP of wave 3 (sheet ^, written x5e in models.cfg): the wreck of SURFACE's grey machine half buried in tan rock
(wave3_i.py), modelled as the sprites look (models.cfg: yaw=0). The kit is wave3_ap_kit.py, the pixels wave3_ap_art.py
(SAND_DMG, in wave3_i_art.SAND's frame).

Each of its six pieces leaves its wreck in its place when destroyed (enemies 245-250, dlevel -1): ^ 77 -> 1, 79 -> 3,
81 -> 5, 115 -> 39, 117 -> 41, 119 -> 43. The machine is smashed: its tower broken off to a jagged stump, its body
caved in and cracked, its two big claws snapped short; the arched grips and the rock round it as before.

- rock_machine_tl_damaged ... rock_machine_br_damaged (^ 1, 3, 5, 39, 41, 43): wave3_i's whole machine (sand_whole),
  wrecked and cut as rock_machine_tl ... _br are (origin).

usage: Blender -b --factory-startup -P wave3_ap_surface.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole sand_damaged --preview <prefix>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, Painter, Frame  # noqa: E402

orig = kit.load("wave3_i")
i = orig.w
kit.forget(i.MODELS, i.WHOLES)

INTACT = Frame(orig.art.SAND, 72, (36, 28))
DAMAGED = kit.frame("SAND_DMG", 72, (36, 28))


def sand_damaged():
    orig.sand_whole()
    i.bake()
    f = DAMAGED
    dmg = kit.Damage(INTACT, DAMAGED)
    # The tower and the claws lose what the damaged sprite leaves out, their broken ends closed and jagged.
    parts = {o.name: o for o in i.meshes()}
    kit.delete_over([parts["tower"], parts["body"]], dmg.gone, close=True)
    kit.delete_over([parts["claws"]], lambda x, y: dmg.gone(x, y) or y < f.Y(46.0), close=True, any_vertex=True)
    for x in (f.X(22.0), f.X(45.0)):
        kit.jag(parts["claws"], (x, f.Y(43.0), 3.0), (0.0, -1.0, 0.0), 1.6, scale=0.8, seed=x)
    kit.jag(parts["tower"], (f.X(34.0), f.Y(4.0), 8.0), (0.0, 0.6, 0.8), 2.2, scale=0.9, seed=2.0)
    p = Painter("sand_dmg", shades={0: (2, 3, 5, 7, 9, 11, 12), 1: (4, 6, 8, 10, 12, 14)}, metallic=0.5,
                roughness=0.4, finish={1: (0.0, 0.85)})
    machine = [o for o in i.meshes() if o.name in ("tower", "body", "claws", "grips")]
    kit.repaint(machine, dmg, p, walls=2, blur=0, probe=0.3, soot=1, soot_radius=1.2, soot_chance=0.6)
    kit.sink([o for o in machine if o.name in ("body", "tower")], dmg, 1.8, min_z=0.5, seed=3.0)
    kit.dent(parts["body"], (f.X(30.0), f.Y(24.0)), 4.0, 1.4, seed=4.0)
    for obj in i.meshes():
        k.smooth(obj, 50)


i.WHOLES["sand_damaged"] = (sand_damaged, (72, 56))
for name, sprite, box in (("rock_machine_tl_damaged", 1, (-36, -12, 0, 28)),
                          ("rock_machine_tc_damaged", 3, (-12, 12, 0, 28)),
                          ("rock_machine_tr_damaged", 5, (12, 36, 0, 28)),
                          ("rock_machine_bl_damaged", 39, (-36, -12, -28, 0)),
                          ("rock_machine_bc_damaged", 41, (-12, 12, -28, 0)),
                          ("rock_machine_br_damaged", 43, (12, 36, -28, 0))):
    i.model(name, [(sprite, True)])(lambda box=box: (sand_damaged(), i.piece(*box)))


if __name__ == "__main__":
    i.run()
