"""Enemies of wave 3, batch R (sheet G: TORM, BOTANY A and B, BONUS), the grey machines on the foliage;
modelled as their sprites look (models.cfg: yaw=0). Objects the game draws from several sprites are built
whole and cut into their pieces, drawn at their own origins (origin) so they meet; the level files' enemy
events say how the pieces are placed. The creatures and ships of sheet G are in wave3_r_beasts.py; the bunker in the cliff
(G 153 above 191) in polish_cliff_bunker.py.

- jaw_gun_a_left, jaw_gun_a_right (G 229 beside G 231) and jaw_gun_b_left, jaw_gun_b_right (G 267 beside
  G 269): the jawed guns lying in TORM's and BOTANY's leaves (events: 753 = 229 at (x, y), 754 = 231 at
  (x + 24, y); 756 = 267, 757 = 269 likewise): a long grey hull, a hooked cap at one end, a lens box and a
  plate on its top, a dark jaw under it with a red glow in its mouth and teeth hanging into the leaves,
  and at the other end an axle out to a bracket that bends down to a red muzzle (its frames flash the
  muzzle and the mouth: both glow). The second gun is the first one mirrored (its sprites are, one pixel
  over). Built whole and cut in two (origin). The leaves round it are the map's: not modelled.
- mortar_breech, mortar_muzzle, mortar_mount, mortar_leaves (G 165 and 167 above G 203 and 205): the
  mortar of TORM, BONUS and BOTANY A (events: 768 = 165 at (x, y - 28), 769 = 167 at (x + 24, y - 28),
  770 = 203 at (x, y), 771 = 205 at (x + 24, y)): a thick grey barrel raised up the screen and to the
  right, a red-ringed muzzle and red lights along it, on a neck down to a mount on the leaves, a red
  light glowing in a slot in its elbow, a fist-like block beside it; the right lower sprite is only
  leaves (its frames flash the muzzle and the lights: they glow). Built whole and cut in four (origin).
  The leaves are the map's (the lower sprites carry a copy of them): not modelled, so the right lower
  piece holds only the bits of the mount that reach into it.

usage: Blender -b --factory-startup -P wave3_r.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole gun_a|gun_b|mortar --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_r_kit as r  # noqa: E402
from wave3_r_kit import k, sh, w, pal  # noqa: E402


# --- G 229 beside G 231 (and G 267 beside G 269, mirrored): the jawed guns ------------------------------

GUN_ORIGIN = (24, 14)  # the art (229 beside 231) is 48 x 28


def gpx(c):
    return c + 0.5 - GUN_ORIGIN[0]


def gpy(row):
    return GUN_ORIGIN[1] - row - 0.5


def hull_along_x(name, sections, mat, segments=32, power=2.6):
    """A hull lying along X: sections (x, y centre, half depth, top z), flat bottom at z = 0; built along
    Y and turned."""
    rings = [k.ring(x, hd, top, segments, z=0.0, x=-yc, top=1.0, bottom=0.02, power=power)
             for x, yc, hd, top in sections]
    first, last = sections[0], sections[-1]
    obj = k.loft(name, rings, mat, start_point=(-first[1], first[0], first[3] * 0.4),
                 end_point=(-last[1], last[0], last[3] * 0.4))
    obj.data.transform(Matrix.Rotation(math.radians(-90), 4, "Z"))
    k.recalc_normals(obj)
    return k.smooth(obj, 45)


def gun_whole(mirrored=False):
    """A long grey hull lying on the leaves, a hook curling down at its left end, a lens box and a plate
    on its top, a dark jaw under it with teeth hanging into the leaves and a red glow in its mouth; at its
    right end an axle out to a bracket that bends down to a red muzzle, an arm on its top. The leaves are
    the map's."""
    gm = r.greys("gun")
    seam = pal("gun_seam", 0x01, metallic=0.3, roughness=0.7)
    lens = pal("gun_lens", 0x0e, metallic=0.1, roughness=0.1, glow=0.5)
    mouth = pal("gun_mouth", 0x72, metallic=0.1, roughness=0.3, glow=0.9)
    mouth_hot = pal("gun_mouth_hot", 0x74, metallic=0.0, roughness=0.3, glow=1.3)
    muzzle = pal("gun_muzzle", 0x75, metallic=0.1, roughness=0.25, glow=1.2)
    muzzle_hot = pal("gun_muzzle_hot", 0x7b, metallic=0.0, roughness=0.2, glow=1.8)

    # The hull: its top along the back (rows 1-6), its front falling to the jaw.
    sections = [(-17.5, 9.4, 2.6, 7.0), (-16.5, 9.5, 3.4, 8.8), (-14.5, 9.6, 3.8, 9.8), (-8.0, 9.7, 3.9, 10.2),
                (0.0, 9.7, 3.9, 10.2), (6.0, 9.7, 3.8, 9.8), (7.6, 9.7, 3.5, 9.0), (8.4, 9.7, 2.8, 7.4)]
    hull = hull_along_x("hull", sections, gm[7], 36)
    w.paint_faces(hull, lambda c, n: gm[0xb] if n.z > 0.45 and n.y > 0.25 and c.y > 11.0 else
                  gm[3] if 10.6 < c.y < 11.6 and n.z > 0.7 and -7.0 < c.x < 3.5 else
                  gm[9] if n.z > 0.75 else gm[5] if n.y < -0.45 else None)
    # The jaw under its front, darker, with the mouth's glow in it.
    jaw = [(-18.0, 4.0, 3.0, 5.2), (-15.5, 3.8, 3.8, 6.6), (-8.0, 3.6, 4.0, 7.2), (2.0, 3.6, 4.0, 7.0),
           (6.6, 3.8, 3.6, 6.2), (7.8, 4.0, 2.6, 4.6)]
    jaw_obj = hull_along_x("jaw", jaw, gm[4], 28, power=3.0)
    w.paint_faces(jaw_obj, lambda c, n: gm[2] if n.y < -0.5 and c.z < 3.0 else gm[5] if n.z > 0.7 else None)
    w.rounded_box("mouth_well", (gpx(22), gpy(12), 5.2), (7.0, 4.0, 4.0), seam, bevel=0.6)
    w.sphere("mouth", (gpx(22), gpy(12.0), 7.0), (3.2, 1.9, 1.2), mouth, 16, 8)
    w.sphere("mouth_hot", (gpx(22.2), gpy(12.0), 7.7), (1.7, 1.0, 0.7), mouth_hot, 12, 6)
    # The grille bars along the jaw's top.
    for c in (11.5, 13.5, 15.5, 17.5, 25.5, 27.5):
        w.rounded_box(f"grille{c}", (gpx(c), gpy(10.0), 7.0), (0.9, 5.0, 0.9), gm[6], bevel=0.3)
    # The teeth: ribs down the jaw's front into the leaves.
    for i, c in enumerate((11.5, 13.5, 15.5, 17.5, 25.5, 27.5)):
        x = gpx(c)
        top = (x, gpy(13.0), 5.2)
        tip = (x + 0.15 * (c - 19), gpy(17.0 + (i % 2)), 0.5)
        w.tube(f"tooth{i}", [top, ((top[0] + tip[0]) / 2, (top[1] + tip[1]) / 2 - 0.3, 4.0), tip], [0.85, 0.75, 0.3],
               gm[5] if i % 2 else gm[6], 8, squash=0.7)
    # The hook curling down at the left end.
    hook = [(gpx(9.0), gpy(3.0), 8.6), (gpx(5.5), gpy(4.0), 8.2), (gpx(3.0), gpy(7.0), 6.8), (gpx(2.6), gpy(10.5), 4.8),
            (gpx(3.6), gpy(13.6), 2.4)]
    pts = w.catmull(hook, 0.6)
    hk = w.tube("hook", pts, [3.0 - 1.2 * (i / (len(pts) - 1)) for i in range(len(pts))], gm[6], 16, squash=0.7)
    w.paint_faces(hk, lambda c, n: gm[0xb] if n.z > 0.5 and n.x < 0.1 else None)
    w.tube("hook_lip", w.catmull([(gpx(9.3), gpy(2.2), 9.4), (gpx(9.6), gpy(5.0), 9.6), (gpx(9.0), gpy(7.5), 8.4)], 0.6),
           0.9, gm[0xc], 10)
    # The lens box and the plate on the top.
    w.rounded_box("lens_box", (gpx(16), gpy(3.6), 10.2), (5.4, 4.0, 2.4), gm[4], bevel=0.6)
    w.sphere("lens", (gpx(16.2), gpy(3.4), 11.2), (1.7, 1.3, 0.8), lens, 14, 7)
    w.rounded_box("plate", (gpx(22), gpy(4.0), 10.3), (6.6, 3.4, 1.4), gm[8], bevel=0.45)
    # The axle out to the bracket, the bracket down to the muzzle, the arm on its top.
    w.lathe_axis("axle", [(0.0, 1.5), (5.6, 1.5), (5.8, 1.9), (6.6, 1.9)], gm[6], (gpx(31.5), gpy(4.0), 7.0),
                 (1, 0, 0), 14)
    br = [(gpx(38.5), gpy(1.2), 10.0), (gpx(38.6), gpy(4.0), 9.6), (gpx(39.0), gpy(7.5), 7.6), (gpx(40.2), gpy(10.0), 5.0)]
    bpts = w.catmull(br, 0.6)
    brk = w.tube("bracket", bpts, 2.1, gm[7], 14, squash=0.55)
    w.paint_faces(brk, lambda c, n: gm[0xa] if n.z > 0.6 and n.x < 0.2 else gm[4] if n.x > 0.5 else None)
    w.rounded_box("arm", (gpx(43.5), gpy(4.6), 7.6), (6.4, 5.6, 3.4), gm[6], bevel=0.9)
    w.rounded_box("arm_top", (gpx(43.8), gpy(3.6), 9.3), (4.4, 2.4, 0.8), gm[9], bevel=0.35)
    # The muzzle at the bracket's foot, pointing down the screen and to the right.
    mz = Vector((gpx(41.2), gpy(11.0), 3.6))
    d = Vector((0.55, -0.75, -0.25)).normalized()
    w.lathe_axis("muzzle_ring", [(-1.2, 1.8), (-0.4, 2.1), (0.6, 2.1), (1.0, 1.7)], gm[4], mz, d, 16)
    w.lathe_axis("muzzle", [(0.6, 1.5), (1.3, 1.3), (1.6, 0.6), (1.7, 0.01)], muzzle, mz, d, 16)
    w.sphere("muzzle_hot", tuple(mz + d * 1.6), (0.8, 0.8, 0.6), muzzle_hot, 10, 5)
    if mirrored:
        r.mirror_x(w.meshes(), -0.5)
    # The leaves round it are the map's (the sprites carry a copy of them): not modelled.


r.whole("gun_a", (48, 28))(lambda: gun_whole(False))
r.whole("gun_b", (48, 28))(lambda: gun_whole(True))


def gun_piece(mirrored, box, centre):
    gun_whole(mirrored)
    w.bake()
    r.cut(w.meshes(), box, centre)
    r.stats_print(*w.meshes())
    r.budget(4800, floor=700)


r.model("jaw_gun_a_left", [(229, True)])(lambda: gun_piece(False, (-24, 0, -14, 14), (-12, 0)))
r.model("jaw_gun_a_right", [(231, True)])(lambda: gun_piece(False, (0, 24, -14, 14), (12, 0)))
r.model("jaw_gun_b_left", [(267, True)])(lambda: gun_piece(True, (-24, 0, -14, 14), (-12, 0)))
r.model("jaw_gun_b_right", [(269, True)])(lambda: gun_piece(True, (0, 24, -14, 14), (12, 0)))


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
