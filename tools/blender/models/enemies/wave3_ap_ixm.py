"""Batch AP of wave 3 (sheet 8): the damaged look of the red machine in IXMUCANE's and SAWBLADES' rock wall
(wave3_y_wall.py), modelled as the sprites look (models.cfg: yaw=0). The kit is wave3_ap_kit.py, the pixels
wave3_ap_art.py (WALL_DMG, in wave3_y_art.WALL's frame).

The slot column's three pieces switch to their damaged sprites when hit hard (enemies 109-111, dlevel 30): 8 277 ->
163, 203 -> 201, 241 -> 239. The machine is burnt out: its red plating gone black, its window dark, glowing cracks
running through what is left; the rock beside it pitted.

- ixm_wall_slot_top_damaged, ixm_wall_slot_mid_damaged, ixm_wall_slot_low_damaged (8 163, 201, 239): wave3_y_wall's
  whole wall (build_wall), damaged as drawn (the damage follows the damaged sprites' pixels), then stood up as the
  intact wall is (wave3_y_wall.upright) and cut as ixm_wall_slot_top, _mid and _low are (origin).

usage: Blender -b --factory-startup -P wave3_ap_ixm.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, w, pal, Painter  # noqa: E402

orig = kit.load("wave3_y_wall")
y = orig.y
n = y.n
kit.forget(n.MODELS, n.OBJECTS)

WALL = orig.WALL
DAMAGED = kit.frame("WALL_DMG", 96, (48, 42))
SLOT_PARTS = ("house", "lip", "window", "band", "panel", "bar_", "well", "grille", "foot")


def wall_damaged():
    orig.build_wall(stand=False)
    w.bake()
    dmg = kit.Damage(WALL, DAMAGED, keep=lambda c, r: 24 <= c < 48)
    slot = [o for o in w.meshes() if o.name.startswith(SLOT_PARTS)]
    rock = [o for o in w.meshes() if o.name.startswith("rock_")]
    # The machine burnt out: its plating black, the window's glowing core gone, the parts the sprite leaves out
    # (its foot is shorter) torn away.
    kit.remove(["window_core"])
    slot = [o for o in w.meshes() if o.name.startswith(SLOT_PARTS)]
    burnt = pal("slot_dmg_burnt", 0x01, metallic=0.25, roughness=0.75)
    for obj in slot:
        obj.data.materials.clear()
        obj.data.materials.append(burnt)
    kit.delete_over(slot, dmg.gone)
    slot = [o for o in w.meshes() if o.name.startswith(SLOT_PARTS)]
    # The glowing cracks: the damaged sprite's red pixels painted over the black (the brighter, the hotter).
    hot = Painter("slot_dmg", shades={7: (2, 4, 6, 8, 10, 12, 14)}, metallic=0.2, roughness=0.4,
                  glow={0x76: 0.6, 0x78: 1.0, 0x7a: 1.5, 0x7c: 2.0, 0x7e: 2.4})
    kit.repaint(slot, dmg, hot, walls=2, blur=0, probe=0.3, keep=lambda obj, index: index >> 4 == 7)
    kit.sink([o for o in slot if o.name.startswith(("house", "window", "band", "panel"))], dmg, 2.4, min_z=2.0,
             seed=1.0, along_normal=False)
    # The rock beside it pitted where the sprite draws holes.
    rp = Painter("wall_dmg_rock", shades={1: (1, 3, 5, 7, 9, 11, 13)}, metallic=0.05, roughness=0.8)
    kit.repaint(rock, dmg, rp, walls=2, blur=0, keep=lambda obj, index: index >> 4 in (0, 1))
    kit.sink(rock, dmg, 1.4, min_z=0.5, seed=2.0)
    for obj in w.meshes():
        k.smooth(obj, 40)
    orig.upright(w.meshes())


PIECES = [(name + "_damaged", box, centre,
           (lambda c0=int(centre[0] - 12 + 48), r0=int(42 - (centre[1] + 14.0)):
            y.frame_mask(DAMAGED, (c0, c0 + 24, r0, r0 + 28))))
          for name, box, centre, _mask in orig.PIECES if "_slot_" in name]
y.pieced("ixm_wall_damaged", wall_damaged, (96, 84), PIECES)


if __name__ == "__main__":
    y.run()
