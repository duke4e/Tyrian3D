"""Batch AO of wave 3, sheet C (DELI, New Deli, BONUS, STATION): the damaged looks of DELI's tower and its long
cannons (wave3_x_tower.py, wave3_x_cannon.py; the burnt gun on its mast: polish_ball_mast_dmg.py), built by those scripts' own builders (imported as
they are, their output unchanged) and damaged as the damaged sprites show (the enemy data's dgr), cut into the same
pieces so that each swaps in place (models.cfg: origin, yaw=0, as the intact pieces). The kit is wave3_ao_kit.py,
the pixels wave3_ao_art.py. (The green twin-tank ship's damaged halves, C 45 47: polish_tank_pod_dmg.py.)

- red_tower_dmg_head, red_tower_dmg_vents, red_tower_dmg_shaft, red_tower_dmg_base (C 91, 129, 93, 131: of 77,
  115, 17, 55, enemies 240, 239, 238, 237): the tower with its head blown off: the dome and the red skirt gone,
  the cup above the crown torn away to a jagged black stump rising to a point, the crown's vents dead,
  dark holes and cracks in the shaft and the bulbs, soot down its front.
- deli_cannon_dmg_breech, _mount, _barrel, _muzzle (C 231, 233, 235, 237: of 269, 271, 273, 275, enemies
  228-231) and deli_cannon_l_dmg_muzzle, _barrel, _mount, _breech (C 276, 277, 279, 281: of 238, 239, 241, 243,
  enemies 232-235): the long cannons cracked and holed, red embers in the cracks, the muzzle's glow out.

usage: Blender -b --factory-startup -P wave3_ao_deli.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole <name> --preview <prefix>]
"""
import os
import sys

import bpy
from mathutils import Vector, noise

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ao_kit as kit  # noqa: E402
from wave3_ao_kit import k, sh, w  # noqa: E402

tower = kit.quiet_import("wave3_x_tower")
cannon = kit.quiet_import("wave3_x_cannon")
x = tower.x  # wave3_x_kit
kit.forget()


def deli_painter(prefix):
    return kit.hot_painter(prefix, {0: (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), 3: (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
                                    4: (4, 5, 6, 7, 8, 9, 10, 11), 5: (0, 1, 2, 3, 4, 5, 6, 7),
                                    6: (1, 2, 3, 4, 5, 6, 7), 8: (2, 3, 4, 5, 6, 7, 8, 9)},
                           metallic=0.45, roughness=0.45, ember=1.1)


def holes_of(fi, fd):
    """Where the damaged sprite draws black over the intact one: holes, pushed in."""
    return kit.field(fi, fd, lambda dv, iv: dv != iv and iv is not None and dv is not None and kit.is_dark(dv) and
                     (dv & 15) <= 1, blur=1)


# --- C 91 above 129 above 93 above 131: the tower, its head blown off ---------------------------------------

TOWER = x.art.TOWER
T_INT = kit.Frame(TOWER, 24, tower.TOWER_ORIGIN)
T_DMG = kit.frame("TOWER_DMG", 24, tower.TOWER_ORIGIN)


def tower_damaged_whole():
    tower.tower_whole()
    w.bake()
    p = deli_painter("aotower")
    fi, fd = T_INT, T_DMG
    # The head is gone: the dome, the skirt and everything on them.
    for obj in kit.meshes():
        if obj.name.split(".")[0] in ("skirt", "dome", "port_rim", "port", "stripe", "dome_rim") or \
                obj.name.startswith("seam"):
            bpy.data.objects.remove(obj)
    # The body broken off at the crown's top (row 28), and on it the torn stump of the head: a jagged black cone
    # rising to a point (the damaged sprite's spike, columns 12-14, row 16).
    start = tower.on_axis(tower.t_of_row(99.5)) - Vector((0, 0, 3.2))
    t0 = tower.t_of_row(99.5)
    top = start + tower.AXIS * (tower.t_of_row(28.2) - t0)
    body = kit.find("body")[0]
    kit.cut_plane(body, top, tower.AXIS)
    kit.jag(body, top, tower.AXIS, 1.4, scale=1.1, seed=3.0)
    t_rim, t_tip = tower.t_of_row(28.6) - t0, tower.t_of_row(15.6) - t0
    prof = [(t_rim, 6.4), (t_rim + 1.0, 6.0), (t_rim + 0.35 * (t_tip - t_rim), 4.2),
            (t_rim + 0.62 * (t_tip - t_rim), 2.2), (t_rim + 0.85 * (t_tip - t_rim), 1.0), (t_tip, 0.15)]
    stump = w.lathe_axis("stump", k.profile(prof, 0.6), p(0x02), tuple(start + Vector((1.0, 0.0, 0.0))),
                         tuple(tower.AXIS), 20, smooth_angle=35)
    off = Vector((2.3, 7.1, 1.7))
    for vt in stump.data.vertices:
        d = vt.co - (start + Vector((1.0, 0.0, 0.0)))
        along = d.dot(tower.AXIS)
        radial = d - tower.AXIS * along
        if radial.length > 0.3:
            n_ = noise.noise(vt.co / 1.3 + off)
            vt.co += radial.normalized() * (1.4 * n_) + tower.AXIS * (0.8 * noise.noise(vt.co / 0.9 - off))
    stump.data.update()
    kit.paint_faces(stump, lambda c, nrm: p(0x07) if nrm.z > 0.75 and nrm.x < -0.2 else p(0x01))
    # Scraps of the dome's plating caught on the rim.
    rim = [top + Vector((dx, dy, 0.6)) for dx, dy in ((-5.4, -0.6), (-3.0, 1.6), (5.8, -1.0), (4.0, 1.8))]
    kit.debris("scrap", [tuple(v) for v in rim], p(0x05), size=(1.6, 2.6), seed=5)
    # The holes and cracks pushed in, everything painted as the damaged sprite draws it.
    holes = holes_of(fi, fd)
    for obj in kit.meshes():
        if obj.name.startswith(("body", "rib", "shoulder", "lamp", "door")):
            kit.sink(obj, holes, 1.3, mode="normal", seed=2.0)
    kit.wreck(kit.meshes(), fi, fd, p, (fi.left(0), fi.right(23), fi.bottom(111), fi.top(0)), keep_floor="tiles",
              delete=False, test=kit.significant)
    # The vents are dead.
    for obj in kit.meshes():
        if obj.name.startswith(("vent_core", "vent-", "vent1")):
            kit.paint_faces(obj, lambda c, nrm: p(0x01))


x.whole("tower_damaged", (24, 112))(tower_damaged_whole)


def tower_damaged_piece(cy):
    tower_damaged_whole()
    x.bake()
    sh.flat_bottom([o for o in x.meshes() if not o.name.startswith("tiles")])
    x.cut(x.meshes(), (-12.0, 12.0, cy - 14.0, cy + 14.0), (0.0, cy))
    x.drop_slivers()
    x.budget(4800)


for _name, _sprite, _cy in (("red_tower_dmg_head", 91, 42.0), ("red_tower_dmg_vents", 129, 14.0),
                            ("red_tower_dmg_shaft", 93, -14.0), ("red_tower_dmg_base", 131, -42.0)):
    x.model(_name, [(_sprite, True)])(lambda cy=_cy: tower_damaged_piece(cy))


# --- C 231 233 235 237 / 276 277 279 281: the long cannons, cracked ----------------------------------------------

C_FRAMES = {False: (kit.Frame(x.art.CANNON, 84, (42, 14)), kit.frame("CANNON_DMG", 84, (42, 14))),
            True: (kit.Frame(x.art.CANNON_L, 84, (42, 14)), kit.frame("CANNON_L_DMG", 84, (42, 14)))}


def cannon_damaged_whole(mirror):
    cannon.cannon_whole(mirror)
    x.bake()
    p = deli_painter("aocannon")
    fi, fd = C_FRAMES[mirror]
    holes = holes_of(fi, fd)
    for obj in kit.meshes():
        kit.sink(obj, holes, 0.8, mode="normal", seed=4.0)
    kit.wreck(kit.meshes(), fi, fd, p, (fi.left(0), fi.right(83), fi.bottom(27), fi.top(0)), keep_floor=None,
              delete=False, test=kit.significant)
    # The muzzle's glow is out: a dim ember in the port.
    for obj in kit.meshes():
        if obj.name.startswith(("port_glow", "port_core")):
            kit.paint_faces(obj, lambda c, nrm: p(0x72) if obj.name.startswith("port_core") else p(0x02))


x.whole("cannon_damaged", (84, 28))(lambda: cannon_damaged_whole(False))
x.whole("cannon_l_damaged", (84, 28))(lambda: cannon_damaged_whole(True))

DMG_NAMES = {"deli_cannon_breech": ("deli_cannon_dmg_breech", 231), "deli_cannon_mount": ("deli_cannon_dmg_mount", 233),
             "deli_cannon_barrel": ("deli_cannon_dmg_barrel", 235), "deli_cannon_muzzle": ("deli_cannon_dmg_muzzle", 237),
             "deli_cannon_l_muzzle": ("deli_cannon_l_dmg_muzzle", 276),
             "deli_cannon_l_barrel": ("deli_cannon_l_dmg_barrel", 277),
             "deli_cannon_l_mount": ("deli_cannon_l_dmg_mount", 279),
             "deli_cannon_l_breech": ("deli_cannon_l_dmg_breech", 281)}


def cannon_damaged_piece(mirror, box, centre):
    cannon_damaged_whole(mirror)
    x.bake()
    x.cut(x.meshes(), box, centre)
    x.budget(4800)


for _name, _sprite, _large, _mirror, _box, _centre in cannon.PIECES:
    _dname, _dsprite = DMG_NAMES[_name]
    x.model(_dname, [(_dsprite, _large)], (24, 28) if _large else (12, 14))(
        lambda m=_mirror, b=_box, c=_centre: cannon_damaged_piece(m, b, c))


if __name__ == "__main__":
    x.run()
