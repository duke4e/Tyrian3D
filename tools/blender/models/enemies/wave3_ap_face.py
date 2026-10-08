"""Batch AP of wave 3 (sheets D and P): the damaged look of the stone face lying on the ground of ASTEROID1 and
ASTEROID2 (wave3_j_rocks.py), modelled as the sprites look (models.cfg: yaw=0). The kit is wave3_ap_kit.py, the
pixels wave3_ap_art.py (FACE_DMG, in wave3_j_art.FACE's frame).

The face's left pieces switch to their damaged sprites when hit hard (enemy 575: D 155 -> 163; 573: D 165 -> 167;
dlevel 10): cracks split the left half of the stone, across the forehead and the brow, down the cheek and the jaw.
The right pieces (P 123, 127) keep their sprites.

- stone_face_tl_damaged, stone_face_bl_damaged (D 163, 167): wave3_j_rocks' whole face (stone_face_whole), cracked
  where the damaged sprites draw it (the cracks cut into the stone, chips at their edges) and cut as stone_face_tl
  and _bl are (origin).

usage: Blender -b --factory-startup -P wave3_ap_face.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole face_damaged --preview <prefix>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ap_kit as kit  # noqa: E402
from wave3_ap_kit import k, w, Painter, Frame  # noqa: E402

orig = kit.load("wave3_j_rocks")
kit.forget(w.MODELS, w.WHOLES)

INTACT = Frame(orig.art.FACE, 48, (24, 28))
DAMAGED = kit.frame("FACE_DMG", 48, (24, 28))


@w.whole("face_damaged", (48, 56))
def face_damaged():
    orig.stone_face_whole()
    w.bake()
    # Every changed pixel counts (the cracks are thin lines of a shade or two).
    dmg = kit.Damage(INTACT, DAMAGED, keep=lambda c, r: c < 24, tolerance=0, despeckle=False)
    p = Painter("face_dmg", shades={0: (2, 3, 4, 5, 6, 7, 8, 9, 10, 11)}, metallic=0.05, roughness=0.75)
    face = w.meshes()
    kit.repaint(face, dmg, p, walls=2, blur=0, probe=0.3, shift=-1.0)
    kit.sink(face, dmg, 1.4, min_z=0.4, seed=1.0, power=0.6)
    for obj in face:
        k.smooth(obj, 50)


def piece(x0, x1, y0, y1):
    face_damaged()
    w.bake()
    w.piece(w.meshes(), x0, x1, y0, y1)


w.model("stone_face_tl_damaged", [(orig.D, 163, True)])(lambda: piece(-24, 0, 0, 28))
w.model("stone_face_bl_damaged", [(orig.D, 167, True)])(lambda: piece(-24, 0, -28, 0))


if __name__ == "__main__":
    w.run()
