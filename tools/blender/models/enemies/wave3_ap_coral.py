"""Batch AP of wave 3 (sheet T): the damaged look of CORAL's purple dome (wave3_v_sea.py; the manta's
head's: polish_coral_manta.py),
modelled as the sprites look (models.cfg: yaw=0). The kit is wave3_ap_kit.py, the pixels wave3_ap_art.py
(CORAL_DOME_DMG, in wave3_v_art's DOME frame).

- coral_dome_tl_damaged, coral_dome_tr_damaged (T 91, 93; the wrecks of 15 and 17, enemies 1201, 1202, dlevel -1):
  wave3_v_sea's whole dome (dome_whole) with its crown blown off: the shell broken open round a dark hollow, the gold
  bands snapped at the break, cut as coral_dome_tl and _tr are (origin); the lower pieces keep their sprites.

usage: Blender -b --factory-startup -P wave3_ap_coral.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, w, pal  # noqa: E402

orig = kit.load("wave3_v_sea")
v = orig.v
n = v.n
kit.forget(n.MODELS, n.OBJECTS)


# --- T 15, 17 -> 91, 93: the dome ----------------------------------------------------------------------------------

DOME_DMG = v.Frame(kit.art.CORAL_DOME_DMG, 48, (24, 28))
WATER = (3, 8)


def dome_damaged():
    orig.dome_whole()
    w.bake()
    f = DOME_DMG
    dmg = kit.Damage(orig.DOME, DOME_DMG, keep=lambda c, r: r < 28)
    paint = v.Painter("dome_dmg", shades={5: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0xb), 1: (2, 4, 6, 8, 0xa)},
                      metallic=0.3, roughness=0.4)

    # (The sprites draw the dome in water, ramps 3 and 8: where the crown was, the damaged sprite draws water.)
    def is_dome(i):
        return i is not None and i >> 4 not in WATER

    def blown_at(x, y):
        c, r = dmg.cell(x, y)
        return r < 28 and is_dome(orig.DOME.get(c, r)) and not is_dome(DOME_DMG.get(c, r))

    def blown(x, y):  # (or a pixel beside it: parts lying over the dome's edge)
        return not is_dome(f.at(x, y)) and f.Y(28.0) < y and any(
            blown_at(x + dx, y + dy) for dx in (-1.2, 0.0, 1.2) for dy in (-1.2, 0.0, 1.2))
    # The bands, the boss and the window snapped off at the break.
    kit.delete_over([o for o in w.meshes() if not o.name.startswith("dome")], blown, close=True, any_vertex=True)
    for obj in kit.named("band_mid"):
        kit.jag(obj, (0.0, f.Y(13.5), 16.0), (0.0, 1.0, 0.0), 1.4, scale=0.6, seed=3.0)
    # The shell's upper half rebuilt as what is left of it: a solid over the damaged sprite's pixels, its top on the
    # dome's curve (so that it meets the lower pieces' shell at the cut), sunk into a hollow where the sprite is
    # dark inside the break.
    cx, cy, rx, ry, height = 0.0, f.Y(28.8), 23.2, 17.8, 17.0

    def zdome(x, y):
        d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        return height * math.sqrt(max(0.0, 1.0 - d)) ** 0.9
    dark = w.sampler(f.g, (f.ox, f.oy), value=lambda i: 1.0 if (i >> 4 not in WATER and i >> 4 not in (1, 5)) or
                     (i >> 4 == 5 and (i & 15) <= 2) else 0.0, blur=1, keep=lambda i: i is not None)
    top = [o for o in kit.named("dome")]
    kit.delete_over(top, lambda x, y: y > 0.0, any_vertex=True)
    polys = kit.z_polys(f, lambda i, c, r: r < 28 and is_dome(i))
    shell = kit.ag.heightfield("dome_top", polys, lambda x, y: max(0.4, zdome(x, y) - 7.0 * dark(x, y) *
                                                                    min(1.0, max(0.0, y) / 3.0)), None, spacing=0.6)
    v.pixelate(shell, f)
    v.paint_sprite(shell, f, paint, wall_steps=-2, keep=is_dome, under=paint(0x50))
    kit.delete_faces_down(shell)
    v.merge_flat(shell)
    for obj in w.meshes():
        k.smooth(obj, 50)


def dome_piece(name, col0):
    x0 = col0 - 24
    return (name, (x0, x0 + 24.0, 0.0, 28.0), (x0 + 12.0, 14.0),
            lambda: DOME_DMG.mask_where(lambda i: i >> 4 not in WATER, (col0, col0 + 24, 0, 28)))


v.pieced("coral_dome_damaged", dome_damaged, (48, 56),
         [dome_piece("coral_dome_tl_damaged", 0), dome_piece("coral_dome_tr_damaged", 24)])


if __name__ == "__main__":
    v.run()
