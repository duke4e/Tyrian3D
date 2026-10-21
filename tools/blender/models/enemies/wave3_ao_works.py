"""Batch AO of wave 3, sheet P (the asteroid levels): the wrecks the works of wave3_w_works.py, wave3_w.py and
wave3_w_launcher.py leave when they are shot (the enemy data's dgr with dlevel -1: the enemy stays, showing its
wreck), and the stone face's damaged look (wave3_j_rocks.py), built by those scripts' own builders (imported as
they are, their output unchanged) and damaged as the sprites show, cut into the same pieces so that each swaps in
place (models.cfg: origin, yaw=0, as the intact pieces). The kit is wave3_ao_kit.py, the pixels wave3_ao_art.py.

- cargo_pod_wreck_tl, cargo_pod_wreck_tr (P 169, 207: the wrecks of 165, 167, enemies 343, 344 and 1035, 1036):
  the cargo pod's back end blown open: two craters torn into its top behind the "812", black inside with an
  ember glowing in the larger one and scraps of plating in it, the plating round them crumpled and sooty, the
  ribs on its right side broken where they cross the hole. The pod's front pieces stay (their dgr is 0).
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
- stone_face_dmg_tr, stone_face_dmg_br (P 125, 129: the damaged looks of 123, 127, enemies 576, 574): the
  stone face's right half cracked, a web of dark cracks across its brow, cheek and jaw.

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
rocks = kit.quiet_import("wave3_j_rocks")
wkit = works.kit
kit.forget()


# --- P 169 207: the cargo pod's wreck ------------------------------------------------------------------

CRATE = wkit.Frame(wkit.art.CRATE, 48, (24, 42))
CRATE_DMG = kit.frame("CRATE_DMG", 48, (24, 42))
SEAM = CRATE.top(28)          # where the wreck's pieces meet the intact front pieces (y = 14)


def taper_to_seam(fld, width=2.0):
    """The field faded out over `width` towards the seam with the intact pieces (so that they meet)."""
    return lambda x, y: fld(x, y) * min(1.0, max(0.0, (y - SEAM) / width))


def crate_wreck():
    works.crate_whole()
    w.bake()
    roof = 10.0
    fi, fd = CRATE, CRATE_DMG

    def hole(dv, iv):
        return dv != iv and dv is not None and ((dv >> 4 == 0 and (dv & 15) <= 3) or kit.is_hot(dv))
    holes = taper_to_seam(kit.field(fi, fd, hole, blur=1))
    crumple = taper_to_seam(kit.field(fi, fd, lambda dv, iv: dv != iv, blur=2))
    box = kit.damage_box(fi, fd, grow=2.0)
    p = kit.hot_painter("aocrate", {0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)}, metallic=0.35, roughness=0.55)

    pod = kit.find("pod")[0]
    kit.pixelate(pod, fi, 1.0, (box[0], box[1], max(box[2], SEAM), box[3]))
    # The craters: the top pushed in deep where the sprite draws the holes, crumpled round them.
    kit.sink(pod, holes, 7.5, min_z=roof + 4.0, seed=1.0, roughness=0.45)
    kit.sink(pod, crumple, 1.2, min_z=roof + 4.0, seed=2.0, roughness=0.6)
    kit.repaint(pod, fi, fd, p, walls=2, pixel=False)
    # The ribs on the right broken where they cross the large hole.
    for rib in kit.find("rib_"):
        kit.pixelate(rib, fi, 1.0, (box[0], box[1], SEAM, box[3]))
        kit.delete_over(rib, lambda c, nrm: holes(c.x, c.y) > 0.35 and c.y > SEAM + 0.5)
    # Scraps of plating in the craters, a few embers among them.
    pts = kit.scatter(holes, (box[0], box[1], SEAM + 1.5, box[3]), 9, 2.6, threshold=0.6, seed=4)
    scraps = kit.debris("scrap", [(x, y, kit.surface_z([pod], x, y, roof + 4.0) + 0.3) for x, y in pts],
                        p(0x06), size=(1.4, 2.8), seed=6)
    for obj in scraps:
        kit.paint_faces(obj, lambda c, nrm: p(0x08) if nrm.z > 0.6 else p(0x04) if nrm.z > -0.3 else p(0x02))
    embers = [(fi.X(c), fi.Y(r), kit.surface_z([pod], fi.X(c), fi.Y(r), roof + 4.0) + 0.1)
              for c, r in ((29.6, 26.4), (30.4, 24.6), (26.5, 23.5))]
    kit.debris("ember", embers, p(0x73), size=(0.8, 1.2), seed=9, flat=0.5)


wkit.pieced("cargo_pod_wreck", crate_wreck, (48, 84), [
    wkit.quarter("cargo_pod_wreck_tl", CRATE_DMG, 0, 0), wkit.quarter("cargo_pod_wreck_tr", CRATE_DMG, 24, 0)])


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


# --- P 125 129: the stone face, cracked (wave3_j_rocks.py) --------------------------------------------------



def face_frames():
    import wave3_j_art
    return kit.Frame(wave3_j_art.FACE, 48, (24, 28)), kit.frame("FACE_DMG", 48, (24, 28))


def stone_face_cracked(x0, x1, y0, y1):
    rocks.stone_face_whole()
    w.bake()
    fi, fd = face_frames()
    p = kit.hot_painter("aoface", {0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)}, metallic=0.05, roughness=0.75)
    face = kit.find("face")[0]
    box = kit.damage_box(fi, fd, grow=1.0)
    kit.pixelate(face, fi, 1.0, box)
    # The cracks: grooves where the damaged sprite draws them darker.
    cracks = kit.field(fi, fd, lambda dv, iv: dv is not None and iv is not None and (dv & 15) + 2 <= (iv & 15), blur=0)
    kit.sink(face, cracks, 0.9, seed=4.0, roughness=0.3)
    kit.repaint(face, fi, fd, p, walls=1, pixel=False)
    w.piece(w.meshes(), x0, x1, y0, y1)


w.model("stone_face_dmg_tr", [("enemy_P", 125, True)])(lambda: stone_face_cracked(0, 24, 0, 28))
w.model("stone_face_dmg_br", [("enemy_P", 129, True)])(lambda: stone_face_cracked(0, 24, -28, 0))


if __name__ == "__main__":
    kit.run()
