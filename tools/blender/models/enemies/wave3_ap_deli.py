"""Batch AP of wave 3 (sheet T): the damaged look of DELI's boss (wave3_v.py) and of its gun arms (wave1_c.py),
modelled as the sprites look (models.cfg: yaw=0). The kit is wave3_ap_kit.py, the pixels wave3_ap_art.py (BOSS_DMG,
in wave3_v_art.BOSS's frame).

When hit hard, six of the boss's twelve pieces switch to their damaged sprites (dgr; enemies 400, 402, 403, 405 of
the top row and the arms 406, 411; dlevel 100): T 1 -> 115, 5 -> 119, 7 -> 121, 11 -> 125, 39 -> 153, 49 -> 163.
The pieces 3 and 9 between them and the bottom row keep their sprites.

- deli_boss_115, deli_boss_119, deli_boss_121, deli_boss_125: wave3_v's whole boss (boss_whole), damaged and cut
  as deli_boss_1, 5, 7, 11 are (origin): its red frame cracked in dark seams, the glossy black spheres cracked
  across in grey lines and dulled (their glints gone), the fire behind the grilles burnt down to dark embers.
- deli_arm_left_damaged, deli_arm_right_damaged (T 153, 163): wave1_c's arms (deli_arm), damaged as the sprites
  show (origin, as deli_arm_left and _right): the eye in the pod put out (a dark socket, the iris a dull ember),
  the pod and the cuff cracked; the right one burnt black over most of its plating.

usage: Blender -b --factory-startup -P wave3_ap_deli.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1] [--whole <prefix>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, w, pal  # noqa: E402

orig = kit.load("wave3_v")
arms = kit.load("wave1_c")
v = orig.v
n = v.n
kit.forget(n.MODELS, n.OBJECTS)

ORIGIN = (72, 28)
BOSS = v.Frame(v.art.BOSS, 144, ORIGIN)
BOSS_DMG = kit.frame("BOSS_DMG", 144, ORIGIN)


def painter():
    """The boss's painter (wave3_v.boss_whole), its fire's glow turned down to embers."""
    return v.Painter("boss_dmg", shades={4: (2, 3, 5, 7, 8, 9, 11, 13), 0: (1, 3, 5, 8, 12), 7: (2, 4, 6, 9, 12)},
                     metallic=0.45, roughness=0.38, finish={0: (0.4, 0.4)},
                     glow={0x70 + s: 0.15 + 0.06 * s for s in range(16)})


def boss_damaged():
    orig.boss_whole()
    w.bake()
    # Only the top row's pieces switch (and the arms, separate models): the damage over rows 0-27.
    dmg = kit.Damage(BOSS, BOSS_DMG, keep=lambda c, r: r < 28)
    kit.remove(["sphere_glint"])
    p = painter()
    parts = w.meshes()
    hole = pal("boss_dmg_hole", 0x01, metallic=0.2, roughness=0.8)
    kit.repaint(parts, dmg, p, walls=2, blur=0, probe=0.4, gone=hole)
    # The right grille blown away: its slats gone, its fire and housing torn out down to the dark core.
    kit.delete_over([o for o in parts if o.name.startswith("slat")], dmg.gone, whole=True)
    kit.delete_over([o for o in w.meshes() if o.name.startswith("vent")], dmg.gone)
    parts = w.meshes()
    # Cracks: pressed into the red plating where the damaged sprite is darker, cut into the black spheres and the
    # canopy where it draws light cracks on them.
    red = [o for o in parts if o.name.split("_m")[0] in ("frame", "plate", "beam", "bend", "pad")]
    kit.sink(red, dmg, 0.7, min_z=-3.0, seed=1.0, min_nz=0.3)
    black = [o for o in parts if o.name.startswith(("sphere", "canopy"))]
    kit.sink(black, dmg, 0.6, min_z=-3.0, mode="lighter", seed=2.0, min_nz=0.2)
    for obj in parts:
        k.smooth(obj, 40)


PIECES = [(115, 0, 0), (119, 48, 0), (121, 72, 0), (125, 120, 0)]


def boss_piece(sprite, col, row):
    x0, y1 = col - ORIGIN[0], ORIGIN[1] - row
    box = (x0, x0 + 24, y1 - 28, y1)
    return (f"deli_boss_{sprite}", box, (x0 + 12, y1 - 14), lambda: BOSS_DMG.mask((col, col + 24, row, row + 28)))


v.PROTECT[:] = ["frame", "plate", "beam", "bend", "pad", "vent_fire", "sphere"]
v.pieced("deli_boss_damaged", boss_damaged, (144, 56), [boss_piece(*p) for p in PIECES])


# --- The arms -----------------------------------------------------------------------------------------------

def arm_damaged(side):
    """wave1_c's arm (left: side 1; right: side -1, mirrored), its eye put out, painted by the damaged sprite where
    it differs from the intact one (the arm's sprite in BOSS's frame: columns 0-23 or 120-143, rows 28-55)."""
    arms.deli_arm(side)
    w.bake()
    origin = (12, 42) if side > 0 else (132, 42)
    c0 = 0 if side > 0 else 120
    intact = v.Frame(v.art.BOSS, 144, origin)
    damaged = kit.frame("BOSS_DMG", 144, origin)
    dmg = kit.Damage(intact, damaged, keep=lambda c, r: c0 <= c < c0 + 24 and r >= 28)
    # The eye: put out.
    socket = pal("arm_dmg_socket", 0x01, metallic=0.2, roughness=0.7)
    ember = pal("arm_dmg_iris", 0x72, metallic=0.2, roughness=0.5, glow=0.25)
    for obj in w.meshes():
        if obj.name.startswith("eye"):
            obj.data.materials.clear()
            obj.data.materials.append(socket)
        elif obj.name.startswith("iris"):
            obj.data.materials.clear()
            obj.data.materials.append(ember)
    p = painter()
    kit.repaint(w.meshes(), dmg, p, walls=2, blur=0, probe=0.4,
                keep=lambda obj, index: not obj.name.startswith(("eye", "iris", "socket")))
    kit.sink([o for o in w.meshes() if o.name.startswith(("pod", "upper_arm", "cuff", "brow"))], dmg, 0.8,
             min_z=-4.0, seed=3.0 + side, min_nz=0.2)
    for obj in w.meshes():
        k.smooth(obj, 50)


n.model("deli_arm_left_damaged", mask=lambda: v.Frame(kit.art.BOSS_DMG, 144, ORIGIN).mask((0, 24, 28, 56)))(
    lambda: arm_damaged(1))
n.model("deli_arm_right_damaged", mask=lambda: v.Frame(kit.art.BOSS_DMG, 144, ORIGIN).mask((120, 144, 28, 56)))(
    lambda: arm_damaged(-1))


if __name__ == "__main__":
    v.run()
