"""Enemies of wave 3, batch R (sheet G: TORM, BOTANY A and B, BONUS), the grey mortar on the foliage (the jawed
guns: polish_jaw_gun.py); modelled as its sprites look (models.cfg: yaw=0). Objects the game draws from several
sprites are built whole and cut into their pieces, drawn at their own origins (origin) so they meet; the level files'
enemy events say how the pieces are placed. The creatures and ships of sheet G are in wave3_r_beasts.py; the bunker in
the cliff (G 153 above 191) in polish_cliff_bunker.py.

- mortar_breech, mortar_muzzle, mortar_mount, mortar_leaves (G 165 and 167 above G 203 and 205): the
  mortar of TORM, BONUS and BOTANY A (events: 768 = 165 at (x, y - 28), 769 = 167 at (x + 24, y - 28),
  770 = 203 at (x, y), 771 = 205 at (x + 24, y)): a thick grey barrel raised up the screen and to the
  right, a red-ringed muzzle and red lights along it, on a neck down to a mount on the leaves, a red
  light glowing in a slot in its elbow, a fist-like block beside it; the right lower sprite is only
  leaves (its frames flash the muzzle and the lights: they glow). Built whole and cut in four (origin).
  The leaves are the map's (the lower sprites carry a copy of them): not modelled, so the right lower
  piece holds only the bits of the mount that reach into it.

usage: Blender -b --factory-startup -P wave3_r.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole mortar --preview <prefix>]
"""
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_r_kit as r  # noqa: E402
from wave3_r_kit import k, sh, w, pal  # noqa: E402


# --- G 165, 167 above G 203, 205: the mortar ---------------------------------------------------------

MORTAR_ORIGIN = (24, 28)  # the art (165, 167 above 203, 205) is 48 x 56


def mpx(c):
    return c + 0.5 - MORTAR_ORIGIN[0]


def mpy(row):
    return MORTAR_ORIGIN[1] - row - 0.5


def frame_along(d):
    """An orthonormal frame (side, d, up) for a direction d (up as close to +Z as possible)."""
    d = Vector(d).normalized()
    side = d.cross(Vector((0, 0, 1)))
    if side.length < 1e-6:
        side = Vector((1, 0, 0))
    side.normalize()
    return side, d, side.cross(d).normalized()


@r.whole("mortar", (48, 56))
def mortar_whole():
    """A thick grey barrel raised up the screen and to the right, its muzzle ringed in red, red lights
    along it, its breech on a neck down to a mount on the leaves: an elbow with a red light glowing in a
    slot, a fist-like block beside it. The leaves round it are the map's."""
    gm = r.greys("mortar")
    seam = pal("mortar_seam", 0x01, metallic=0.3, roughness=0.7)
    red = pal("mortar_red", 0x72, metallic=0.3, roughness=0.35)
    light = pal("mortar_light", 0x75, metallic=0.0, roughness=0.3, glow=1.1)
    light_hot = pal("mortar_light_hot", 0x7a, metallic=0.0, roughness=0.25, glow=1.6)

    # The leaves round its mount are the map's (the lower sprites carry a copy of them): not modelled.

    # The barrel: from its breech over the neck up to the muzzle (the sprite's diagonal, raised).
    B = Vector((mpx(17.9), mpy(31.4), 8.0))
    T = Vector((mpx(34.6), mpy(16.4), 20.6))
    side, D, up = frame_along(T - B)
    L = (T - B).length
    prof = [(-2.6, 2.8), (-2.0, 4.8), (-0.8, 5.4), (L * 0.35, 5.5), (L * 0.7, 5.3), (L - 3.0, 5.0), (L - 2.4, 4.6)]
    barrel = w.lathe_axis("barrel", k.profile(prof, 0.8), gm[7], B, D, 32, smooth_angle=40)

    def barrel_paint(c, n):
        # Lit along its upper left (the sprite's light edge), darker on the lower right.
        lean = n.dot(Vector((-0.7, 0.7, 0.0)).normalized())
        if n.z > 0.4 and lean > 0.3:
            return gm[0xb]
        if n.z > 0.7:
            return gm[9]
        if lean < -0.3:
            return gm[5]
        return None
    w.paint_faces(barrel, barrel_paint)
    # Bands round it and the muzzle's red ring.
    for t, rad, m_ in ((L * 0.18, 5.7, gm[4]), (L * 0.58, 5.6, gm[4])):
        w.lathe_axis(f"band{t:.0f}", [(t - 0.5, rad - 0.3), (t - 0.3, rad), (t + 0.3, rad), (t + 0.5, rad - 0.3)], m_, B,
                     D, 32)
    w.lathe_axis("muzzle", [(L - 2.8, 4.7), (L - 2.5, 5.1), (L - 0.6, 5.0), (L - 0.1, 4.4), (L + 0.1, 2.8),
                            (L + 0.15, 0.01)], red, B, D, 28)
    w.lathe_axis("bore", [(L - 0.2, 2.4), (L + 0.2, 2.4), (L + 0.25, 0.01)], seam, B, D, 20)
    # The red lights along its top (rows 23-26): two slots, glowing.
    for t, off, size in ((L * 0.42, -2.6, 1.4), (L * 0.36, 2.4, 1.2)):
        n = (up * 4.7 + side * off).normalized()
        c = B + D * t + n * 5.15
        lens = w.sphere(f"light{t:.0f}", (0, 0, 0), (size * 0.8, size * 1.6, 0.55), light, 12, 6)
        frame = Matrix((side.to_4d(), D.to_4d(), n.to_4d(), (0, 0, 0, 1))).transposed()
        frame.translation = c
        lens.data.transform(frame)
        core = w.sphere(f"light_core{t:.0f}", (0, 0, 0), (size * 0.4, size * 0.9, 0.4), light_hot, 10, 5)
        frame.translation = c + n * 0.25
        core.data.transform(frame)

    # The neck from the breech down to the elbow.
    neck = [tuple(B - D * 1.5), (mpx(12.0), mpy(35.0), 6.2), (mpx(8.0), mpy(39.0), 4.6)]
    pts = w.catmull(neck, 0.6)
    nk = w.tube("neck", pts, [4.4 - 0.8 * i / (len(pts) - 1) for i in range(len(pts))], gm[7], 18, squash=0.8)
    w.paint_faces(nk, lambda c, n: gm[9] if n.z > 0.5 and n.x - n.y < 0.2 else gm[4] if n.x - n.y > 0.8 else None)
    # The elbow on the leaves, the red slot in it.
    elbow = w.block("elbow", (mpx(4.5), mpy(43.0)), 4.6, 6.0, 6.0, gm[6], taper=1.0, rounding=2.0, power=3.0,
                    segments=32, z0=0.4)
    w.paint_faces(elbow, lambda c, n: gm[0xa] if n.z > 0.5 and c.x < mpx(4) else gm[4] if n.x > 0.5 else None)
    w.rounded_box("slot", (mpx(7.5), mpy(45.5), 5.0), (2.6, 8.0, 2.2), seam, bevel=0.4)
    w.rounded_box("slot_light", (mpx(7.5), mpy(45.5), 5.6), (1.6, 7.0, 1.4), light, bevel=0.4)
    w.rounded_box("slot_core", (mpx(7.5), mpy(44.5), 6.1), (0.7, 3.0, 0.8), light_hot, bevel=0.25)
    # The fist-like block beside it: a block with three knuckles on its top.
    fist = w.block("fist", (mpx(16.0), mpy(44.5)), 6.4, 5.6, 5.0, gm[6], taper=0.6, rounding=1.6, power=3.5,
                   segments=32, z0=0.4)
    w.paint_faces(fist, lambda c, n: gm[8] if n.z > 0.7 else gm[4] if n.y < -0.5 or n.x > 0.5 else None)
    for i, c in enumerate((12.5, 15.5, 18.5)):
        w.lathe_axis(f"knuckle{i}", [(0.0, 1.2), (0.3, 1.5), (5.0, 1.5), (5.4, 1.1)], gm[9] if i != 1 else gm[7],
                     (mpx(c), mpy(40.5), 5.4), (0, -1, 0), 12, squash=0.8)
    w.rounded_box("wrist", (mpx(11.0), mpy(40.0), 4.2), (5.0, 4.4, 3.0), gm[5], bevel=0.8)


def mortar_piece(box, centre):
    mortar_whole()
    w.bake()
    r.cut(w.meshes(), box, centre)
    r.stats_print(*w.meshes())
    r.budget(4800, floor=700)


r.model("mortar_breech", [(165, True)])(lambda: mortar_piece((-24, 0, 0, 28), (-12, 14)))
r.model("mortar_muzzle", [(167, True)])(lambda: mortar_piece((0, 24, 0, 28), (12, 14)))
r.model("mortar_mount", [(203, True)])(lambda: mortar_piece((-24, 0, -28, 0), (-12, -14)))
r.model("mortar_leaves", [(205, True)])(lambda: mortar_piece((0, 24, -28, 0), (12, -14)))


if __name__ == "__main__":
    r.run()
