"""Enemies of wave 3, batch M (sheet J: TORM, BONUS, BOTANY A), the grey machines on the foliage; modelled
as their sprites look (models.cfg: yaw=0). The green machines are in wave3_m.py, the big green shell
in wave3_m_shell.py.

- window_block_tl, window_block_tr, window_block_bl, window_block_br (J 5, 7, 43, 45): the grey
  building of TORM and BONUS, which event 12 places as four sprites (5 and 7 above 43 and 45): a
  tall spine with three green windows glowing in its roof (its frames light them one after the
  other), a roof sloping down to the left, a ribbed block with a pipe along it at the right and a
  plinth with vents in front; built whole and cut (origin). The patch of foliage the sprites draw it on
  is the map's ground (the game draws it under the building), so the model has none.
- field_gun_barrel, field_gun_breech, field_gun_mount (J 89; J 127 and 129 below it): the heavy grey
  gun of TORM, BONUS and BOTANY A, which the events place as 89 above 127 with 129 to its right
  (and an empty sprite, 119, for the muzzle flash): a long barrel with a red tip and two red lights
  along it, raised up the screen to the left on a curved neck from a base on the ground (the sprites'
  foliage is the map's, not modelled), a red light glowing in the base (its frames brighten it as it
  fires); built whole and cut (origin).
- lens_pad (J 77): the grey pad on the ground of TORM and BONUS, an oval puck with a green lens glowing
  in a ringed socket in it (its frames brighten the lens).
- eye_orb (J 83): the grey armoured orb of TORM on its brackets on the ground (the sprite's foliage is
  the map's, not modelled), open on its red eye (its frames open the shell and light the eye: the model
  shows it open, the eye glowing).

usage: Blender -b --factory-startup -P wave3_m_ground.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole block|gun --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_m_kit as w  # noqa: E402
from wave3_m_kit import art, k, sh, pal, px, py, model, whole, J  # noqa: E402


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


# --- J 5, 7 above 43, 45: the window block -------------------------------------------------------------

BLOCK_ORIGIN = (24, 28)


@whole("block", (48, 56))
def block_whole():
    """A grey building on the foliage: a tall spine with three green windows glowing in its roof
    between a light frame and a pillar, a roof sloping down to the left of it, a ribbed block with
    a pipe along it at the right, and a plinth with vents and a light ledge in front."""
    m = greys("block")
    window = pal("block_window", 0xc8, metallic=0.1, roughness=0.12, glow=1.0)
    window_lit = pal("block_window_lit", 0xcc, metallic=0.1, roughness=0.1, glow=1.6)
    # No foliage under it: the sprite's patch of leaves is the map's ground, which the game draws under it
    # (batch AV); the building stands on the ground, every part down to z 0.

    # The plinth along the front, under everything.
    plinth = wedge("plinth", [(-20.2, -19.2), (14.6, -19.2), (16.6, -16.4), (16.6, -4.0), (-20.2, -4.0)],
                     lambda x, y: 7.0 if y > -15.2 else 7.0 - (-15.2 - y) * 1.1, m["grey"], bevel=0.45, z0=0.0)
    w.paint_faces(plinth, lambda c, n: m["dark"] if n.y < -0.5 else m["light"] if n.z > 0.5 and c.y < -14.0 else None)
    # The ledge along the plinth's front and the vents in its top.
    w.rounded_box("ledge", (-1.8, -15.0, 6.9), (36.0, 1.6, 1.2), m["pale"], bevel=0.4)
    for x0, x1 in ((-18.6, -12.4), (-7.0, 0.2), (2.2, 8.4)):
        w.rounded_box(f"vent{x0}", ((x0 + x1) / 2, -11.2, 6.7), (x1 - x0, 3.6, 1.0), m["black"], bevel=0.3)
        for i in range(3):
            x = x0 + (x1 - x0) * (i + 0.5) / 3
            w.rounded_box(f"vent_slat{x0}{i}", (x, -11.2, 7.1), (0.9, 3.0, 0.9), m["mid"], bevel=0.25)

    # The roof sloping down to the left, and its rim.
    def slope(x, y):
        return 8.0 + 8.0 * min(1.0, max(0.0, (x + 19.6) / 8.6))
    roof = wedge("roof", [(-20.2, -6.0), (-10.6, -6.0), (-10.6, 24.0), (-20.2, 13.8)], slope, m["grey"], bevel=0.5,
                   z0=0.0)
    w.paint_faces(roof, lambda c, n: m["mid"] if n.z > 0.5 and c.y > 6.0 else m["dark"] if n.z < 0.3 else None)
    w.tube("roof_rim", [(-19.6, -5.5, 8.4), (-19.6, 13.6, 8.4), (-11.0, 23.4, 15.6)], 0.6, m["pale"], 8)
    # The pillar and the spine with the windows.
    w.rounded_box("pillar", (-9.0, 8.6, 9.5), (3.4, 30.4, 19.0), m["light"], bevel=0.6)
    spine = w.rounded_box("spine", (-3.4, 9.0, 9.0), (8.4, 30.0, 18.0), m["mid"], bevel=0.6)
    w.rounded_box("spine_cap", (-4.6, 22.6, 18.4), (12.4, 2.8, 1.6), m["pale"], bevel=0.5)
    w.rounded_box("frame", (1.4, 8.6, 9.2), (2.0, 30.4, 18.4), m["grey"], bevel=0.5)
    for (y0, y1), lit in (((14.2, 20.8), True), ((6.2, 11.8), False), ((-2.2, 2.8), False)):
        w.rounded_box(f"window_well{y0}", (-3.6, (y0 + y1) / 2, 17.5), (6.6, y1 - y0 + 0.8, 1.4), m["black"], bevel=0.3)
        w.rounded_box(f"window{y0}", (-3.6, (y0 + y1) / 2, 17.9), (5.8, y1 - y0, 0.9), window_lit if lit else window,
                      bevel=0.25)
    for y in (12.8, 4.2):
        w.rounded_box(f"window_bar{y}", (-3.6, y, 18.1), (7.4, 1.6, 1.0), m["pale"], bevel=0.35)
    # The ribbed block at the right with the pipe along it.
    right = w.rounded_box("right", (9.1, 6.0, 7.2), (15.2, 30.0, 14.4), m["grey"], bevel=0.7)
    w.paint_faces(right, lambda c, n: m["dark"] if n.x > 0.6 or n.y < -0.6 else None)
    for y in (17.0, 12.4, 7.4, 2.4, -3.2):
        w.lathe_axis(f"rib{y}", [(0.0, 0.01), (0.2, 1.0), (13.2, 1.0), (13.4, 0.01)], m["light"], (2.4, y, 14.2),
                     (1, 0, 0), 12, squash=0.8)
    w.tube("pipe", [(11.0, 20.4, 15.6), (11.0, 6.0, 16.0), (11.0, -8.2, 15.4), (11.0, -9.6, 12.6)], 1.55, m["pale"], 14)
    for y in (16.0, 1.0):
        w.lathe_axis(f"pipe_clamp{y}", [(-0.6, 1.6), (-0.4, 2.0), (0.4, 2.0), (0.6, 1.6)], m["dark"], (11.0, y, 15.8),
                     (0, 1, 0), 14)


def block_piece(x0, x1, y0, y1):
    block_whole()
    w.bake()
    w.piece(w.meshes(), x0, x1, y0, y1)


model("window_block_tl", [(J, 5, True)])(lambda: block_piece(-24, 0, 0, 28))
model("window_block_tr", [(J, 7, True)])(lambda: block_piece(0, 24, 0, 28))
model("window_block_bl", [(J, 43, True)])(lambda: block_piece(-24, 0, -28, 0))
model("window_block_br", [(J, 45, True)])(lambda: block_piece(0, 24, -28, 0))


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


# --- J 77: the lens pad -----------------------------------------------------------------------------

@model("lens_pad", [(J, 77, True)])
def lens_pad():
    """A grey oval pad with a lip round its top and a green lens glowing in a ringed socket in it,
    standing on the ground in the lower half of its sprite."""
    g = w.grid(art.J77, 24)
    m = greys("pad")
    lens = pal("pad_lens", 0xc9, metallic=0.1, roughness=0.08, glow=1.2)
    lens_core = pal("pad_lens_core", 0xcd, metallic=0.0, roughness=0.05, glow=1.8)
    pad = w.block("pad", (px(11.5), py(20.6)), 8.9, 6.3, 3.9, m["grey"], taper=0.6, rounding=1.7, power=2.7,
                  segments=48, dome=0.4)
    w.paint_faces(pad, lambda c, n: m["dark"] if n.y < -0.5 else m["mid"] if n.z > 0.85 else
                  m["light"] if n.y > 0.4 and n.z < 0.85 else None)
    w.hoop("rim", (px(11.5), py(20.6), 3.4), [(6.2, -0.3), (6.9, -0.2), (6.9, 0.35), (6.3, 0.4)], m["pale"], 48,
           scale_y=0.66)
    cx, cy = px(10.6), py(19.2)
    w.hoop("socket", (cx, cy, 3.9), [(3.2, -0.6), (4.6, -0.3), (4.8, 0.35), (4.1, 0.55), (3.3, 0.2)], m["pale"], 32,
           scale_y=0.62)
    w.sphere("socket_floor", (cx, cy, 3.6), (3.6, 2.3, 0.6), m["black"], 20, 8)
    w.sphere("lens", (cx, cy, 3.8), (2.9, 1.8, 1.2), lens, 20, 10)
    w.sphere("lens_core", (cx - 0.6, cy + 0.3, 4.7), (1.2, 0.7, 0.4), lens_core, 12, 6)


# --- J 83: the eye orb -----------------------------------------------------------------------------

@model("eye_orb", [(J, 83, True)])
def eye_orb():
    """A grey armoured orb on the foliage, held in brackets at its lower right; its shell is drawn
    back from its front, where a red eye glows in a dark socket, seams running round it."""
    m = greys("orb")
    eye = pal("orb_eye", 0x77, metallic=0.0, roughness=0.15, glow=1.3)
    eye_core = pal("orb_eye_core", 0x7b, metallic=0.0, roughness=0.1, glow=1.8)
    shell_edge = pal("orb_shell_edge", 0x0b, metallic=0.65, roughness=0.25)

    # No foliage under it: the sprite's leaves are the map's ground, which the game draws under it (batch AV);
    # the orb stands on its brackets on the ground.
    cx, cy, rad = px(10.5), py(10.5), 8.6
    orb = w.sphere("orb", (cx, cy, 8.4), (rad, rad, 7.6), m["mid"], 36, 18)
    w.paint_faces(orb, lambda c, n: m["light"] if n.z > 0.75 and n.x < 0.2 else m["dark"] if n.z < 0.1 else None)
    # The seams: one round its middle, one over its top.
    w.tube("seam_round", [(cx + (rad + 0.05) * math.cos(a), cy + (rad + 0.05) * math.sin(a), 8.4)
                          for a in [math.radians(t) for t in range(0, 361, 15)]], 0.35, m["darker"], 6)
    w.tube("seam_top", [(cx + 0.0, cy + (rad + 0.02) * math.cos(a), 8.4 + 7.62 * math.sin(a))
                        for a in [math.radians(t) for t in range(0, 181, 12)]], 0.32, m["darker"], 6)
    # The eye: a socket in the front (down the screen and to the left), the shell's rim round it.
    d = Vector((-0.28, 0.12, 0.95)).normalized()
    centre = Vector((cx, cy, 8.4)) + Vector((d.x * rad, d.y * rad, d.z * 7.6)) * 0.86
    socket = w.sphere("socket", (0, 0, 0), (3.6, 3.6, 1.2), m["black"], 20, 8)
    lens_ = w.sphere("eye", (0, 0, 0), (2.8, 2.8, 1.5), eye, 20, 10)
    core = w.sphere("eye_core", (0, 0, 0), (1.1, 1.1, 0.6), eye_core, 12, 6)
    rim = w.hoop("eye_rim", (0, 0, 0), [(3.4, -0.5), (4.3, -0.2), (4.2, 0.45), (3.5, 0.5)], shell_edge, 28)
    z = Vector((0, 0, 1))
    rot = z.rotation_difference(d).to_matrix().to_4x4()
    for obj, lift in ((socket, 0.0), (lens_, 0.4), (core, 1.5), (rim, 0.4)):
        obj.data.transform(Matrix.Translation(centre) @ rot @ Matrix.Translation((0, 0, lift)))
    core.data.transform(Matrix.Translation((-0.5, 0.4, 0.0)))
    # The brackets at the lower right holding it, down to the foliage.
    for i, (a, b) in enumerate((((6.5, -3.0, 4.0), (9.2, -5.2, 0.8)), ((3.0, -6.8, 4.0), (5.0, -9.6, 0.8)),
                                ((7.6, 1.2, 4.6), (10.4, 0.6, 0.8)))):
        w.tube(f"bracket{i}", [a, ((a[0] + b[0]) / 2 + 0.6, (a[1] + b[1]) / 2 - 0.4, a[2] - 0.6), b], 1.0, m["grey"], 10)
        w.sphere(f"bracket_foot{i}", b, (1.5, 1.5, 0.8), m["dark"], 10, 5)


w.run()
