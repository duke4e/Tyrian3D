"""Enemies of wave 3, batch W (sheet P: the asteroid levels), modelled as their sprites look (models.cfg:
yaw=0): the block house and the small blocks with doors. The works built on the block house (the
drilling rig, the bronze pump with its golden dome, the cargo pod) are in wave3_w_works.py, the tan
launcher in wave3_w_launcher.py; the kit is wave3_w_kit.py, the pixels wave3_w_art.py.

- block_house_tl, block_house_tr, block_house_bl, block_house_br (P 153, 155 above 191, 193): the grey
  block house of ASTEROID2, ASTEROID?, ASTCITY and AST. CITY (enemies 313-316, which event 12 places as
  the sheet arranges them): a block 40 x 43 pixels with rounded corners standing on the ground, its roof
  laid with fifteen raised panels; three of them are hatches the frames sink (157/161 and their
  neighbours), set a little lower in dark gaps. Built whole and cut into its pieces (origin).
- block_door (P 279): ASTEROID?'s small block in the floor with a lid over a well in its top; the frames
  lift the lid (281, 245, 283): the model shows it a little open over a dark slit.
- block_slot (P 53): the same block with its lid open, standing up the screen over the dark well.

The asteroid floor the sprites draw round these (map tile 372) is the map's ground, which the game draws under
them: the models have none of it (batch AV), the blocks stand on the ground (z 0).

usage: Blender -b --factory-startup -P wave3_w.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_w_kit as kit  # noqa: E402
from wave3_w_kit import art, k, sh, w, p, pal  # noqa: E402


# --- P 153 155 / 191 193: the block house ------------------------------------------------------------

HOUSE = kit.Frame(art.BLOCKS, 48, (24, 28))


def block_house_whole():
    # No floor round it: the sprites' floor is the map's ground, which the game draws under it (batch AV).
    parts, _ = kit.house("house", HOUSE, 0)


kit.pieced("block_house", block_house_whole, (48, 56), [
    kit.quarter("block_house_tl", HOUSE, 0, 0), kit.quarter("block_house_tr", HOUSE, 24, 0),
    kit.quarter("block_house_bl", HOUSE, 0, 28), kit.quarter("block_house_br", HOUSE, 24, 28)])


# --- P 279 and P 53: the small blocks with doors -------------------------------------------------------

def small_block(prefix, f, angle, glow=0.0):
    """The small block of the asteroid floor (columns 4-19, rows 0-14 of its sprite) with a well in its top
    (columns 7-16, rows 2-12) closed by a lid hinged at its far edge, opened by `angle` degrees (the
    sprites draw the opened lid standing up the screen over a dark opening); a dim red light far down in
    the well (glow)."""
    m = kit.house_mats(prefix)
    g = m["grey"]
    height = 7.0
    outline = kit.rrect(f.left(4), f.right(19), f.bottom(14), f.top(0), (2.0, 2.0, 1.4, 1.2))
    body = kit.slab(prefix + "_body", outline, 0.0, height, m["wall"], bevel=0.8, segments=3)
    fx0, fx1, fy0, fy1 = f.left(7), f.right(16), f.bottom(12), f.top(2)
    kit.cut_hole(body, fx0, fx1, fy0, fy1, height - 3.0, height + 1.0)

    def paint_body(c, nrm):
        if nrm.z > 0.95:
            return m["roof"] if c.z > height - 0.5 else g[2]
        inside = fx0 - 0.01 <= c.x <= fx1 + 0.01 and fy0 - 0.01 <= c.y <= fy1 + 0.01
        if inside:  # the well's walls: the far one lit, the others dark
            return g[6] if nrm.y < -0.5 else g[3]
        if nrm.z > 0.3:
            return m["lit"] if (nrm.x < -0.25 or nrm.y > 0.25) else m["shade"]
        return m["wall"]
    kit.paint_faces(body, paint_body)
    # The lid: a plate with a grip across its near end, hinged at the well's far edge.
    lid = [p.chamfered(prefix + "_lid", kit.rrect(fx0 + 0.35, fx1 - 0.35, fy0 + 0.35, fy1 - 0.15), height - 0.9,
                       height - 0.1, m["roof"], chamfer=0.3)]
    kit.paint_plate(lid[0], m)
    lid.append(kit.rounded_box(prefix + "_grip", ((fx0 + fx1) / 2, fy0 + 1.5, height - 0.05),
                               (fx1 - fx0 - 3.4, 0.9, 0.45), g[0xc], bevel=0.2))
    for x in (fx0 + 1.6, fx1 - 1.6):
        lid.append(kit.rounded_box(f"{prefix}_hinge{x:.0f}", (x, fy1 - 0.4, height - 0.25), (1.6, 1.0, 0.9), g[5],
                                   bevel=0.3))
    kit.rotate_about(lid, "X", -math.radians(angle), (0.0, fy1 - 0.4, height - 0.25))
    if glow:
        w.sphere(prefix + "_inner", ((fx0 + fx1) / 2, (fy0 + fy1) / 2 - 1.0, height - 2.9), (2.6, 2.2, 0.25),
                 pal(prefix + "_inner", 0x74, metallic=0.0, roughness=0.5, glow=glow), 12, 5)
    # No floor round it: the sprite's floor is the map's ground, which the game draws under it (batch AV).
    kit.merge()


DOOR = kit.Frame(art.DOOR, 24, (12, 14))
SLOT = kit.Frame(art.HATCH53, 24, (12, 14))


@kit.model("block_door", mask=lambda: DOOR.mask())
def block_door():
    small_block("bdoor", DOOR, 14.0, 0.5)


@kit.model("block_slot", mask=lambda: SLOT.mask())
def block_slot():
    small_block("bslot", SLOT, 62.0, 0.8)


kit.run()
