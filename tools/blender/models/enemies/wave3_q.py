"""Batch Q of wave 3 (sheet A: APPROACH, MISTAKES, SOH JIN, GAUNTLET), the steel shells; modelled as their
sprites look (models.cfg: yaw=0). The mace, its chain and anchor and the skull chest are in
wave3_q_mace.py, SOH JIN's bronze pieces in wave3_q_bronze.py.

- fire_housing_l_top, fire_housing_l_bottom (A 229 above 267) and their mirror images fire_housing_r_top,
  fire_housing_r_bottom (A 9 above 47): the steel housings the fire flaps (fire_flap_*, wave2_h.py) are
  hinged to, at the sides of APPROACH's, MISTAKES' and SOH JIN's fire gates: the levels put the left
  housing at the left edge with the flap A 237 / 275 beside it, and the flap A 7 / 45 beside the right
  housing at the right edge, each two sprites tall. A half dome, its flat side against the flap's hinge,
  like a steel fish's head: an eye in a socket near its top, a pillar of two ribs and a bracket along
  the flat side (one rib on down to the bottom), and a crease sweeping round its cheek. Built whole and
  cut into the two sprites' pieces (origin).
- hinge_pod_l, hinge_pod_r (A 161 beside 163, mirror images): the small steel pod of SOH JIN and
  GAUNTLET, two short housings back to back round a hinge whose ends glow red. SOH JIN puts the halves
  side by side; GAUNTLET sends single halves across the screen. Built whole and cut in two (origin).
- missile_sign_left, missile_sign_right (A 49 beside 51): SOH JIN's red "WARNING / MISSILE SHIPS!!"
  sign, glowing red letter strokes, built whole and cut in two (origin).

usage: Blender -b --factory-startup -P wave3_q.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole housing|pod|sign --preview <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_q_kit as q  # noqa: E402
from wave3_q_kit import art, k, sh, pal  # noqa: E402


def steel_mats(prefix):
    m = {s: pal(f"{prefix}_steel{s}", 0x60 | s, metallic=0.55, roughness=0.34) for s in range(3, 14)}
    m["rib"] = pal(f"{prefix}_rib", 0x6d, metallic=0.6, roughness=0.26)
    m["rib_dark"] = pal(f"{prefix}_rib_dark", 0x69, metallic=0.6, roughness=0.3)
    m["seam"] = pal(f"{prefix}_seam", 0x62, metallic=0.4, roughness=0.5)
    m["socket"] = pal(f"{prefix}_socket", 0x61, metallic=0.3, roughness=0.45)
    m["eye"] = pal(f"{prefix}_eye", 0x62, metallic=0.35, roughness=0.08)
    m["rivet"] = pal(f"{prefix}_rivet", 0x6e, metallic=0.6, roughness=0.2)
    return m


def paint_shell(obj, shade, m, dents=(), lo=3, hi=13, squeeze=0.8):
    """Paints a steel shell in the sprite's shades (pulled towards the middle, the model's own light
    does the rest); faces inside a dent (cx, cy, rx, ry) take the socket's colour."""
    def pick(c, n):
        for cx, cy, rx, ry in dents:
            if math.hypot((c.x - cx) / rx, (c.y - cy) / ry) < 0.85 and n.z > -0.2:
                return m["socket"]
        if n.z < -0.5:
            return m[lo + 1]
        s = 8.0 + (shade(c.x, c.y) - 8.0) * squeeze
        if n.z < 0.3:
            s -= 1.0
        return m[int(min(hi, max(lo, round(s))))]
    q.paint_faces(obj, pick)


# --- A 229 / 267 (and A 9 / 47): the fire gates' housings --------------------------------------------

HOUSING_ORIGIN = (12, 28)  # the art: A 229 above 267, 24 x 56
HOUSING_FLAT = 11.6        # the flat side, against the flap's hinge (x = 12)
HOUSING_EYE = (-0.6, 15.3, 2.5, 3.5)


@q.whole("housing", (24, 56))
def housing_whole():
    g = q.grid(art.HOUSING, 24)
    m = steel_mats("fh")
    dome = q.HalfDome(HOUSING_FLAT, 0.0, 23.0, 22.4, 12.0, p=2.55, q=2.3, e=0.55)
    ex, ey, erx, ery = HOUSING_EYE

    def surface(x, y):
        return dome(x, y) - q.ellipse_dent(x, y, ex, ey, erx, ery, 1.7)

    polys = [q.clamp_poly(p, x_max=HOUSING_FLAT) for p in q.pixel_polys(g, lambda v, c, r: True, HOUSING_ORIGIN)]
    shell = q.heightfield("shell", polys, surface, m[8], spacing=0.5)
    q.w.simplify_bottom(shell)
    shade = q.shades(g, HOUSING_ORIGIN, keep=lambda v: v >> 4 == 6, blur=3)
    paint_shell(shell, shade, m, dents=[(ex, ey, erx, ery)])
    q.decimate(shell, 5200)
    parts = [shell]

    # The eye: a glossy dark ball in its socket, a rivet above it.
    parts.append(q.sphere("eye", (ex + 0.15, ey + 0.4, surface(ex, ey) + 0.35), (1.9, 2.3, 1.35), m["eye"], 24, 12))
    parts.append(q.sphere("rivet", (0.4, 18.7, dome(0.4, 18.7) + 0.1), (0.65, 0.65, 0.5), m["rivet"], 12, 6))

    # The pillar along the flat side: two ribs in the upper half, the outer one on down to the bottom;
    # a bracket where the inner one ends.
    parts.append(q.rib("rib_in", 3.1, 5.9, 5.6, 19.4, dome, 0.85, m["rib"]))
    parts.append(q.rib("rib_out", 7.0, 9.0, -18.0, 19.6, dome, 0.75, m["rib"]))
    parts.append(q.rib("rib_edge", 10.0, 11.4, -15.0, 17.5, dome, 0.35, m["rib_dark"], columns=5))
    bx, by = 3.9, 3.0
    parts.append(q.block("bracket", (bx, by), 2.1, 2.3, 1.9, m["rib_dark"], taper=0.5, rounding=0.8, power=3.0,
                         z0=dome(bx, by) - 0.7, dome=0.3))
    parts.append(q.lathe_axis("bracket_pin", [(-1.3, 0.55), (-1.1, 0.75), (1.1, 0.75), (1.3, 0.55)], m["rib"],
                              (bx, by, dome(bx, by) + 1.25), (1, 0, 0), 14))

    # The creases round the cheek and the lower plate.
    parts.append(q.groove("crease_cheek", [(-10.6, 5.5), (-8.0, 3.2), (-5.2, 0.2), (-2.6, -2.8), (0.8, -4.6), (6.6, -5.0)],
                          surface, m["seam"], radius=0.5, sink=0.2))
    parts.append(q.groove("crease_low", [(-7.8, -5.4), (-4.6, -8.4), (-1.0, -10.0), (2.8, -10.6), (6.6, -10.4)],
                          surface, m["seam"], radius=0.42, sink=0.22))
    return parts


HOUSING_PIECES = [("top", 14.0, (-14.0, 14.0, 0.0, 30.0)), ("bottom", -14.0, (-14.0, 14.0, -30.0, 0.0))]


def housing_piece(cy, box, mirror):
    objects = housing_whole()
    if mirror:
        q.mirror_x(objects)
    q.cut(objects, box, (0.0, cy))
    q.budget(4800)


for _side, _sprites, _mirror in (("l", (229, 267), False), ("r", (9, 47), True)):
    for (_piece, _cy, _box), _sprite in zip(HOUSING_PIECES, _sprites):
        q.model(f"fire_housing_{_side}_{_piece}", [(_sprite, True)])(
            lambda cy=_cy, box=_box, mirror=_mirror: housing_piece(cy, box, mirror))


# --- A 161 / 163: the hinged pod -------------------------------------------------------------------

POD_ORIGIN = (24, 14)  # the art: A 161 beside 163, 48 x 28
POD_FLAT = -0.95       # the left half's flat side; the hinge lies between the halves, at x = 0
POD_EYE = (-12.4, 2.6, 2.2, 2.5)


@q.whole("pod", (48, 28))
def pod_whole():
    g = q.grid(art.CAPSULE, 48)
    m = steel_mats("hp")
    hot = pal("hp_hinge_hot", 0x75, metallic=0.2, roughness=0.3, glow=1.1)
    hinge = pal("hp_hinge", 0x0a, metallic=0.65, roughness=0.25)
    dome = q.HalfDome(POD_FLAT, 0.0, 17.4, 8.4, 7.6, p=2.4, q=2.3, e=0.55)
    ex, ey, erx, ery = POD_EYE

    def surface(x, y):
        return dome(x, y) - q.ellipse_dent(x, y, ex, ey, erx, ery, 1.3)

    left = [q.clamp_poly(p, x_max=POD_FLAT) for p in q.pixel_polys(g, lambda v, c, r: c <= 23, POD_ORIGIN)]
    shell = q.heightfield("shell", left, surface, m[8], spacing=0.4)
    q.w.simplify_bottom(shell)
    shade = q.shades(g, POD_ORIGIN, keep=lambda v: v >> 4 == 6, blur=3)
    paint_shell(shell, shade, m, dents=[(ex, ey, erx, ery)])
    q.decimate(shell, 3200)
    parts = [shell,
             q.sphere("eye", (ex + 0.1, ey + 0.3, surface(ex, ey) + 0.3), (1.6, 1.8, 1.1), m["eye"], 20, 10),
             q.rib("rib_in", -8.9, -6.2, 0.6, 6.4, dome, 0.6, m["rib"]),
             q.rib("rib_out", -5.0, -3.1, -4.6, 6.6, dome, 0.55, m["rib"]),
             q.rib("rib_edge", -2.0, -1.05, -4.0, 5.2, dome, 0.3, m["rib_dark"], columns=5)]
    for obj in parts:
        q.sh.apply_modifiers(obj)
    mirrored = [k.mirror_x(obj, obj.name + "_r") for obj in parts]
    # The hinge between the halves: a steel barrel, its ends glowing red.
    z = 5.6
    parts.append(q.lathe_axis("hinge", [(0.0, 0.9), (0.25, 1.25), (7.15, 1.25), (7.4, 0.9)], hinge, (0.0, -3.4, z),
                              (0, 1, 0), 20))
    for name, y0, d in (("hinge_end_top", 3.9, 1), ("hinge_end_bottom", -3.3, -1)):
        parts.append(q.lathe_axis(name, [(0.0, 1.05), (0.6, 1.05), (1.1, 0.75), (1.35, 0.01)], hot, (0.0, y0, z),
                                  (0, d, 0), 18))
    for i, y in enumerate((-1.4, 0.6, 2.4)):
        parts.append(q.lathe_axis(f"hinge_ring{i}", [(-0.18, 1.2), (-0.1, 1.42), (0.1, 1.42), (0.18, 1.2)], m["rib"],
                                  (0.0, y, z), (0, 1, 0), 20))
    return parts + mirrored


def pod_piece(cx, box):
    objects = pod_whole()
    q.cut(objects, box, (cx, 0.0))
    q.budget(4000)


for _name, _sprite, _cx, _box in (("hinge_pod_l", 161, -12.0, (-26.0, 0.0, -16.0, 16.0)),
                                  ("hinge_pod_r", 163, 12.0, (0.0, 26.0, -16.0, 16.0))):
    q.model(_name, [(_sprite, True)])(lambda cx=_cx, box=_box: pod_piece(cx, box))


# --- A 49 / 51: the MISSILE SHIPS sign -------------------------------------------------------------

@q.whole("sign", (48, 28))
def sign_whole():
    """Glowing red strokes, the letters' left sides (shade 6) a darker red, as the sprite draws them."""
    g = q.grid(art.SIGN, 48)
    origin = (24, 14)
    rows = q.regions(g, lambda v, c, r: "R")
    strokes = q.part("letters", rows, "R", None, sh.round_profile(3.0, max_height=1.5, min_height=1.2),
                     origin=origin, base=0.0, bottom=0.35, smooth=0, epsilon=0.12, spacing=0.3, rim=0.1, sigma=0.6)
    q.decimate(strokes, 6000)
    shade = q.shades(g, origin, keep=lambda v: True, blur=0)
    bands = [(0.0, pal("sign_red5", 0x75, metallic=0.1, roughness=0.35, glow=0.5)),
             (6.5, pal("sign_red6", 0x76, metallic=0.1, roughness=0.32, glow=0.65)),
             (7.5, pal("sign_red8", 0x78, metallic=0.1, roughness=0.3, glow=0.85))]
    q.paint_bands(strokes, lambda c, n: shade(c.x, c.y) - (2.0 if n.z < 0.3 else 0.0), bands)
    return [strokes]


def sign_piece(cx, box):
    objects = sign_whole()
    q.cut(objects, (box[0], box[1], -14.0, 14.0), (cx, 0.0))


for _name, _sprite, _cx, _box in (("missile_sign_left", 49, -12.0, (-24.0, 0.0)),
                                  ("missile_sign_right", 51, 12.0, (0.0, 24.0))):
    q.model(_name, [(_sprite, True)])(lambda cx=_cx, box=_box: sign_piece(cx, box))


if __name__ == "__main__":
    q.run()
