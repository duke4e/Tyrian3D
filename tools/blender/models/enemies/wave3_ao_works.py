"""Batch AO of wave 3, sheet P (the asteroid levels): the wrecks the works of wave3_w_works.py, wave3_w.py and
wave3_w_launcher.py leave when they are shot (the enemy data's dgr with dlevel -1: the enemy stays, showing its
wreck), built by those scripts' own builders (imported as
they are, their output unchanged) and damaged as the sprites show, cut into the same pieces so that each swaps in
place (models.cfg: origin, yaw=0, as the intact pieces). The kit is wave3_ao_kit.py, the pixels wave3_ao_art.py.

- pump_dome_wreck (P 121: the wreck of the golden dome 115, enemy 338): the onion dome burnt black-brown,
  holed and dented, a red-hot gash down its right side (upright on the shaft as the intact dome: damaged
  laid where the sprites draw it, then stood up again).
- asteroid_rig_wreck_crane_l, asteroid_rig_wreck_crane_r (P 47, 49: the wrecks of the crane's halves 9, 11,
  enemies 332, 333 and 1024, 1025): the brown head scorched in its middle, the bent pipe on its left snapped,
  the two stays on the right broken off under the head (the derrick upright as the intact one: damaged laid
  where the sprites draw it, then stood up again).
- tan_launcher_wreck (P 235: the wreck of the tan launcher 277, enemy 197): its barrels blown out of the
  housing, the bores torn open and burnt.
- block_wreck (P 87: the wreck of the small block with the lid, 279 and 53, enemies 198 and 457): the lid
  blown off, a burnt crater where the well was.

usage: Blender -b --factory-startup -P wave3_ao_works.py -- [--only names] [--preview <prefix>] [--check 1]
       [--whole <prefix>]
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ao_kit as kit  # noqa: E402
from wave3_ao_kit import w, n  # noqa: E402

works = kit.quiet_import("wave3_w_works")
blocks = kit.quiet_import("wave3_w")
launcher = kit.quiet_import("wave3_w_launcher")
wkit = works.kit
kit.forget()


# --- P 47 49: the drilling rig's crane, wrecked ----------------------------------------------------------

RIG = wkit.Frame(wkit.art.RIG, 48, (24, 42))
RIG_DMG = kit.frame("RIG_DMG", 48, (24, 42))


def rig_wreck():
    works.rig_whole()
    w.bake()
    fi, fd = RIG, RIG_DMG
    p = kit.hot_painter("aorig", {0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12), 1: (0, 1, 2, 3, 4, 5, 6, 7, 9),
                                  0xa: (1, 2, 3, 5, 7, 9)}, metallic=0.4, roughness=0.55)
    # The crane's halves only (rows 0-27): the head scorched, the bent pipe snapped, the right stays broken off.
    # The derrick stands upright over the bore hole (batch AV): damaged laid where the sprites draw it, leaning
    # up the screen, then stood up again.
    box = (fi.left(0), fi.right(47), fi.top(28) + 0.05, fi.top(0))
    works.RIG_DRAWN.drawn(kit.meshes())
    kit.wreck(kit.meshes(), fi, fd, p, box)
    works.RIG_DRAWN.upright(kit.meshes())


# Cut as the intact crane's halves are (wave3_w_works.drawn_pieced): the head and the stays' upper parts.
works.drawn_pieced("asteroid_rig_wreck", rig_wreck, (48, 84), [
    wkit.quarter("asteroid_rig_wreck_crane_l", RIG_DMG, 0, 0), wkit.quarter("asteroid_rig_wreck_crane_r", RIG_DMG, 24, 0)],
    works.RIG_DRAWN)


# --- P 87: the small block's wreck --------------------------------------------------------------------------

DOOR = wkit.Frame(wkit.art.DOOR, 24, (12, 14))
DOOR_DMG = kit.frame("DOOR_DMG", 24, (12, 14))


@wkit.model("block_wreck", mask=lambda: DOOR_DMG.mask())
def block_wreck():
    blocks.small_block("bwreck", DOOR, 0.0, 0.0)
    w.bake()
    for obj in kit.meshes():
        if obj.name.startswith(("bwreck_lid", "bwreck_grip", "bwreck_hinge", "bwreck_inner")):
            bpy.data.objects.remove(obj)
    fi, fd = DOOR, DOOR_DMG
    p = kit.hot_painter("aoblock", {0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)}, metallic=0.3, roughness=0.6)
    crater = kit.field(fi, fd, lambda dv, iv: dv != iv and dv is not None and (dv & 15) <= 3, blur=1)
    body = kit.find("bwreck_body")[0]
    box = kit.damage_box(fi, fd, grow=1.0)
    kit.pixelate(body, fi, 1.0, box)
    kit.sink(body, crater, 2.6, min_z=4.5, seed=2.0, roughness=0.5)
    kit.repaint(body, fi, fd, p, walls=2, pixel=False)
    # A few scraps of the lid in the well.
    pts = kit.scatter(crater, box, 4, 2.4, threshold=0.6, seed=8)
    scraps = kit.debris("bwreck_scrap", [(x, y, 4.4) for x, y in pts], p(0x05), size=(1.4, 2.4), seed=3)
    for obj in scraps:
        kit.paint_faces(obj, lambda c, nrm: p(0x07) if nrm.z > 0.6 else p(0x03))
    n.merge_by_material()


# --- P 235: the tan launcher's wreck ------------------------------------------------------------------------

LAUNCHER = wkit.Frame(wkit.art.LAUNCHER, 24, (12, 14))
LAUNCHER_DMG = kit.frame("LAUNCHER_DMG", 24, (12, 14))


@wkit.model("tan_launcher_wreck", mask=lambda: LAUNCHER_DMG.mask())
def tan_launcher_wreck():
    launcher.tan_launcher()
    w.bake()
    # The barrels thrown out of the housing (their bores 6 rows further down the screen), as the wreck draws them.
    elevation = math.radians(40.0)
    d = Vector((0.0, -math.cos(elevation), math.sin(elevation)))
    shift = d * (5.5 / math.cos(elevation)) * 0.8
    for obj in kit.meshes():
        if obj.name.startswith(("sleeve_", "bore_", "ring_")):
            obj.data.transform(Matrix.Translation(shift))
    fi, fd = LAUNCHER, LAUNCHER_DMG
    p = kit.hot_painter("aolaunch", {0xa: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb), 6: (0, 1, 2, 3, 4, 6, 8, 0xa),
                                     0: (1, 2, 3, 5, 7)}, metallic=0.4, roughness=0.5)
    kit.wreck(kit.meshes(), fi, fd, p, (fi.left(0), fi.right(23), fi.bottom(27), fi.top(0)), keep_floor="tl_floor")
    for obj in kit.find("bore_"):
        kit.paint_faces(obj, lambda c, nrm: p(0x72))


if __name__ == "__main__":
    kit.run()
