"""Enemies of wave 3, batch M (sheet J: TORM, BONUS, BOTANY A), the grey machines on the foliage; modelled
as their sprites look (models.cfg: yaw=0). The green machines are in wave3_m.py, the big green shell
in wave3_m_shell.py. (The grey building with the green windows, J 5, 7, 43, 45: polish_window_block.py; TORM's eye orb, J 83 and its
frames: polish_eye_orb.py.)

- field_gun_barrel, field_gun_breech, field_gun_mount (J 89; J 127 and 129 below it): the heavy grey
  gun of TORM, BONUS and BOTANY A, which the events place as 89 above 127 with 129 to its right
  (and an empty sprite, 119, for the muzzle flash): a long barrel with a red tip and two red lights
  along it, raised up the screen to the left on a curved neck from a base on the ground (the sprites'
  foliage is the map's, not modelled), a red light glowing in the base (its frames brighten it as it
  fires); built whole and cut (origin).

usage: Blender -b --factory-startup -P wave3_m_ground.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole gun --preview <prefix>]
"""
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_m_kit as w  # noqa: E402
from wave3_m_kit import art, k, sh, pal, model, whole, J  # noqa: E402,F401  (art: wave3_ap_torm.py reads ground.art)


def greys(prefix):
    return {
        "black": pal(f"{prefix}_black", 0x01, metallic=0.5, roughness=0.5),
        "darker": pal(f"{prefix}_grey3", 0x03, metallic=0.55, roughness=0.45),
        "dark": pal(f"{prefix}_grey5", 0x05, metallic=0.6, roughness=0.4),
        "grey": pal(f"{prefix}_grey7", 0x07, metallic=0.6, roughness=0.38),
        "mid": pal(f"{prefix}_grey9", 0x09, metallic=0.6, roughness=0.35),
        "light": pal(f"{prefix}_greya", 0x0a, metallic=0.6, roughness=0.32),
        "pale": pal(f"{prefix}_greyc", 0x0c, metallic=0.6, roughness=0.28),
    }


def wedge(name, outline, z_of, mat, bevel=0.0, z0=0.0):
    """A block over the outline (counter-clockwise) from z0 up to a top shaped by z_of(x, y)."""
    obj = k.slab(name, outline, z0, z0 + 1.0, mat)
    for v in obj.data.vertices:
        if v.co.z > z0 + 0.5:
            v.co.z = z_of(v.co.x, v.co.y)
    if bevel:
        k.bevel(obj, bevel, 2)
        sh.apply_modifiers(obj)
    return k.smooth(obj, 35)


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def inside(poly, x, y):
    hit = False
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[i - 1]
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            hit = not hit
    return hit


# --- J 89 above 127, with 129 at its right: the field gun --------------------------------------------

GUN_ORIGIN = (36, 28)


@whole("gun", (72, 56))
def gun_whole():
    """A long grey barrel raised up the screen to the left, a red tip and two red lights along it,
    its rear narrowing into a curved neck down to a base of two blocks standing on the foliage, a
    red light glowing in a slot in the right one."""
    m = greys("gun")
    red = pal("gun_red", 0x74, metallic=0.4, roughness=0.35)
    red_dark = pal("gun_red_dark", 0x72, metallic=0.4, roughness=0.4)
    light = pal("gun_light", 0x77, metallic=0.0, roughness=0.3, glow=1.3)
    light_core = pal("gun_light_core", 0x7a, metallic=0.0, roughness=0.3, glow=1.6)
    bore = pal("gun_bore", 0x01, metallic=0.3, roughness=0.7)
    # No foliage under the mount: the sprites' leaves are the map's ground, which the game draws under it
    # (batch AV); the base stands on the ground.
    # The base: a foot at the left, the housing with the light at the right.
    foot = w.block("foot", (5.0, -17.2), 4.4, 5.2, 5.6, m["grey"], taper=0.8, rounding=1.6, power=3.0, segments=32,
                   z0=0.0)
    house = w.block("house", (14.6, -16.0), 5.8, 6.2, 7.6, m["grey"], taper=1.0, rounding=2.0, power=3.0, segments=32,
                    z0=0.0)
    for obj in (foot, house):
        w.paint_faces(obj, lambda c, n: m["mid"] if n.z > 0.8 else m["dark"] if n.y < -0.5 or n.x > 0.6 else None)
    w.rounded_box("light_slot", (16.9, -17.6, 6.0), (3.4, 8.4, 3.0), m["black"], bevel=0.4)
    w.rounded_box("light", (16.9, -17.6, 6.7), (2.2, 7.2, 2.0), light, bevel=0.5)
    w.rounded_box("light_core", (16.9, -16.4, 7.3), (0.9, 2.6, 1.0), light_core, bevel=0.3)
    # The barrel, raised up the screen to the left; its rear narrows into a curved neck down to the base.
    B = Vector((6.4, -2.6, 9.4))
    M = Vector((-9.2, 13.4, 20.6))
    D = (M - B).normalized()
    plan = Vector((D.x, D.y, 0.0)).normalized()
    side = Vector((plan.y, -plan.x, 0.0))
    up = side.cross(D).normalized()
    L = (M - B).length
    barrel = [(-3.4, 3.4), (-1.6, 4.2), (0.0, 5.0), (L * 0.4, 5.1), (L - 4.0, 4.6), (L - 1.6, 3.9), (L - 1.0, 3.3)]
    obj = w.lathe_axis("barrel", k.profile(barrel, 0.8), m["grey"], B, D, 32, smooth_angle=40)
    w.paint_faces(obj, lambda c, n: m["light"] if n.z > 0.85 else m["dark"] if n.z < -0.2 else None)
    w.lathe_axis("tip", [(L - 1.4, 3.6), (L - 0.6, 3.6), (L + 0.2, 3.0), (L + 0.6, 1.8), (L + 0.7, 0.01)], red, B, D, 28)
    w.lathe_axis("tip_ring", [(L - 2.4, 4.0), (L - 2.2, 4.4), (L - 1.4, 4.4), (L - 1.2, 3.9)], m["darker"], B, D, 28)
    w.lathe_axis("bore", [(L + 0.45, 1.2), (L + 0.75, 1.2), (L + 0.8, 0.01)], bore, B, D, 16)
    # The two red lights along its top and a ridge between them.
    for t, off, size in ((L * 0.72, 1.4, 1.5), (L * 0.32, -1.8, 1.6)):
        p = B + D * t + side * off
        n = (up * 4.6 + side * off).normalized()
        c = B + D * t + n * (5.0 - 0.35)
        lens = w.sphere(f"red_light{t:.0f}", (0, 0, 0), (size, size * 1.5, 0.75), red_dark, 12, 6)
        frame = Matrix((side.to_4d(), D.to_4d(), n.to_4d(), (0, 0, 0, 1))).transposed()
        frame.translation = c
        lens.data.transform(frame)
        glow = w.sphere(f"red_light_core{t:.0f}", (0, 0, 0), (size * 0.6, size * 1.0, 0.6), red, 10, 5)
        glow.data.transform(frame @ Matrix.Translation((0, 0, 0.3)))
    w.tube("barrel_ridge", [B + D * 2.0 + up * 5.15, B + D * (L * 0.6) + up * 5.0], 0.55, m["pale"], 8)
    # The neck: from the barrel's rear down and round to the base.
    rear = B - D * 2.6
    w.tube("neck", w.catmull([rear, (9.6, -7.0, 8.4), (11.4, -11.4, 6.0), (11.8, -15.0, 3.6)], 0.7), 3.9, m["mid"], 16)
    w.tube("neck_edge", w.catmull([rear + Vector((1.6, 0.4, 2.0)), (11.0, -6.8, 10.4), (13.2, -11.4, 8.2),
                                   (13.6, -14.2, 6.2)], 0.7), 0.9, m["pale"], 8)
    w.lathe_axis("neck_collar", [(-0.5, 3.6), (-0.3, 4.2), (0.9, 4.2), (1.1, 3.6)], m["dark"], rear + D * 0.2, D, 24)


def gun_piece(x0, x1, y0, y1):
    gun_whole()
    w.bake()
    w.piece(w.meshes(), x0, x1, y0, y1)


model("field_gun_barrel", [(J, 89, True)])(lambda: gun_piece(-12, 12, 0, 28))
model("field_gun_breech", [(J, 127, True)])(lambda: gun_piece(-12, 12, -28, 0))
model("field_gun_mount", [(J, 129, True)])(lambda: gun_piece(12, 36, -28, 0))


w.run()
