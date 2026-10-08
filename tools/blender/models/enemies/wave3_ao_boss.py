"""Batch AO of wave 3, sheet 4: the tusked boss's damaged look (TYRIAN, TYRIAN X, HOLES, ASSASSIN), built by
wave3_ab_boss.py's own builder (imported as it is, its output unchanged) from the damaged sprites' pixels and cut
into the same pieces, drawn at their own origins (origin) so that each swaps in place (models.cfg: yaw=0, as the
intact pieces). The kit is wave3_ao_kit.py, the pixels wave3_ao_art.py (BOSS_DMG).

When the boss is beaten hard the level's linked pieces switch to their damaged sprites together (the enemy data's
dgr): 10 -> 162, 12 -> 164, 16 -> 168, 18 -> 170, 48 -> 200, 56 -> 208, 88 -> 240, 90 -> 242, 92 -> 244,
94 -> 246; 86, 126 and 130 switch to empty sprites (238, 278, 282), 124 and 132 (dgr 0) are taken away, 128 (the
jaw, boss_chin) switches to 280, the same picture; 14, 50, 54 and the core keep theirs.

- tusk_boss_162 ... tusk_boss_246: the boss wrecked: both claws blown off with their tusks and hooks, leaving
  torn stumps of the gold struts and scraps of the claw blocks; the right engine block's cable and the right
  wing's tip shot away; holes blasted into both engine blocks and beside the left one; the gold wings and struts
  scorched brown. The relief of plates is the intact builder's, over the damaged sprite's outline and painted by
  its pixels; the holes are pushed into it; the torn edges roughened.
- 280 (the jaw) is the intact jaw's picture: models.cfg gives it boss_chin.

usage: Blender -b --factory-startup -P wave3_ao_boss.py -- [--only names] [--preview <prefix>] [--check 1]
       [--whole <prefix>]
"""
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ao_kit as kit  # noqa: E402
from wave3_ao_kit import k, sh, w, n  # noqa: E402

boss = kit.quiet_import("wave3_ab_boss")
ab = boss.ab
kit.forget()

ORIGIN = (60, 56)
INTACT = boss.BOSS
DMG = ab.Frame(kit.art.BOSS_DMG, 120, ORIGIN)
DMG_PAINT = ab.Frame(kit.art.BOSS_DMG, 120, ORIGIN).fill({0x01, 0x02})


def boss_damaged():
    saved = boss.BOSS, boss.PAINT, n.merge_by_material, sh.inflate
    inflate = sh.inflate

    def inflate_or_empty(name, polys, *args, **kw):
        """The damaged sprite has no claws, so no red panels on them: an empty part instead."""
        if not polys:
            return k.mesh_object(name, [], [], args[0] if args else None)
        return inflate(name, polys, *args, **kw)
    boss.BOSS, boss.PAINT, sh.inflate = DMG, DMG_PAINT, inflate_or_empty
    n.merge_by_material = lambda objects=None: None
    try:
        boss.build_boss()
    finally:
        boss.BOSS, boss.PAINT, n.merge_by_material, sh.inflate = saved
    w.bake()
    for obj in kit.meshes():
        if not obj.data.polygons:
            bpy.data.objects.remove(obj)
    # Gone with the claws: the tusks and the hooks; the right cable with the right wing's tip.
    for obj in kit.meshes():
        if obj.name.split(".")[0] in ("tusk", "tusk_m", "hook", "hook_m", "cable_m"):
            bpy.data.objects.remove(obj)
    fi, fd = INTACT, DMG
    # The holes blasted into the plates (black where the intact sprite has plating), the torn stumps roughened.
    holes = kit.field(fi, fd, lambda dv, iv: iv is not None and dv is not None and dv != iv and kit.is_dark(dv) and
                      (dv & 15) <= 1, blur=1)
    torn = kit.field(fi, fd, lambda dv, iv: dv != iv and dv is not None and iv is not None, blur=1)
    for obj in kit.meshes():
        if obj.name.split(".")[0] != "plates":
            continue
        box = kit.damage_box(fi, fd, grow=1.0)
        kit.pixelate(obj, fi, 1.0, box)
        kit.sink(obj, holes, 3.2, min_z=1.5, seed=1.0, roughness=0.5)
        kit.sink(obj, torn, 0.9, min_z=1.5, seed=6.0, roughness=1.0, scale=0.9)
        p = boss.painter()
        ab.paint(obj, DMG_PAINT, p, wall_steps=2, under=p(0x02), wall_z=0.8)
        kit.merge_flat(obj)
    n.merge_by_material()


DAMAGED = {10: 162, 12: 164, 16: 168, 18: 170, 48: 200, 56: 208, 88: 240, 90: 242, 92: 244, 94: 246}


def damaged_piece(sprite, pc, pr):
    x0, y1 = pc - 60.0, 56.0 - pr
    return (f"tusk_boss_{DAMAGED[sprite]}", (x0, x0 + 24.0, y1 - 28.0, y1), (x0 + 12.0, y1 - 14.0),
            lambda: ab.frame_mask(DMG, (pc, pc + 24, pr, pr + 28)))


ab.pieced("tusk_boss_damaged", boss_damaged, (120, 112),
          [damaged_piece(*pc) for pc in boss.BOSS_PIECES if pc[0] in DAMAGED])


if __name__ == "__main__":
    kit.run()
