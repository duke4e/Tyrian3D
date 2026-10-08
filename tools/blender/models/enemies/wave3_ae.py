"""Enemies of wave 3, batch AE (sheet ', written x27 in models.cfg): FRUIT's flying fruit, modelled as their
sprites look (models.cfg: yaw=0). The kit is wave3_ae_kit.py, the pixels wave3_ae_art.py; FRUIT's lemon beetle
and strawberry wing are in wave3_ae_lemon.py, CORAL's eel, worm and egg in wave3_ae_coral.py, FRUIT's pineapple
boss in wave3_ae_boss.py. Objects the levels put together from several sprites (the level files' enemy events
say how) are built whole and cut into their pieces, drawn at their own origins (origin).

- orange_saw_tl, orange_saw_tr, orange_saw_bl, orange_saw_br (' 78, 80 above 116, 118; enemies 1229-1232 at
  (x, y - 28), (x + 24, y - 28), (x, y), (x + 24, y), in the sky): a dimpled orange on a steel saw plate whose
  eight curved blades sweep up a little towards their tips. Its frames (82 84 120 122) turn the blades by a
  sixteenth of a turn; the pieces keep them still. Built whole and cut in four (origin).
- berry_ring (' 169, enemy 1226, in the sky): a red twin berry in a bevelled grey ring, held by four gold
  prongs.
- grape_wing_l, grape_wing_r (' 130, 132; enemies 1227, 1228 at (x, y), (x + 24, y), in the sky or on the
  ground): a bunch of pale grapes round a glossy pod, two grapes hanging from curled stalks under it, on a dark
  purple wing with a spur at each tip. Built whole and cut in two (origin).

usage: Blender -b --factory-startup -P wave3_ae.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ae_kit as kit  # noqa: E402
from wave3_ae_kit import k, sh, w, pal, Painter  # noqa: E402


# --- ' 78 80 / 116 118: the bladed orange ---------------------------------------------------------------

SAW = kit.frame("SUN", 48, (24, 28))
ORANGE_C = Vector((0.5, 0.0, 9.6))
ORANGE_R = (10.7, 10.6, 9.6)


def orange_saw_whole():
    f = SAW
    # The saw plate: every pixel of the sprite (the blades and, under the orange, their hub), thin, its spine
    # raised; the blades sweep up towards their tips.
    polys = kit.outlines_of(f, lambda val, c, r: True, smooth=2, epsilon=0.25, min_area=2.0)
    steel = pal("saw_steel", 0x0c, metallic=0.6, roughness=0.28)
    edge = pal("saw_edge", 0x09, metallic=0.6, roughness=0.3)
    under = pal("saw_under", 0x06, metallic=0.5, roughness=0.4)
    blades = kit.plate("saw_plate", polys, steel, 0.55, ORANGE_C.z - 0.2, aspect=0.3, rim=0.12, spacing=0.5)
    # The hub under the orange is never seen: left out.
    kit.delete_faces(blades, lambda c, nrm: math.hypot(c.x - ORANGE_C.x, c.y - ORANGE_C.y) < 8.0)

    def sweep(x, y, z):
        r = math.hypot(x - ORANGE_C.x, y - ORANGE_C.y)
        return 2.4 * kit.smoothstep(9.0, 24.0, r)
    kit.displace_z(blades, sweep)
    kit.paint_faces(blades, lambda c, nrm: under if nrm.z < -0.3 else (edge if nrm.z < 0.55 else steel))
    # The orange: a dimpled ball, painted by the sprite's oranges.
    peel = Painter("orange", shades={7: (4, 5, 6, 7, 8, 9, 0xa, 0xb)}, metallic=0.0, roughness=0.55)
    ball = w.sphere("orange", tuple(ORANGE_C), ORANGE_R, peel(0x78), 64, 32)
    kit.bumps(ball, 0.16, 1.1, seed=3.0, centre=ORANGE_C)
    kit.paint_sprite(ball, f, peel, wall_steps=-1, keep=lambda val: val >> 4 == 7, default=peel(0x77), blur=2,
                     probe=-1.0)
    # A steel collar where the blades leave the peel.
    collar = pal("saw_collar", 0x07, metallic=0.6, roughness=0.35)
    kit.torus("saw_collar", (ORANGE_C.x, ORANGE_C.y, ORANGE_C.z + 0.1), ORANGE_R[0] - 0.7, 0.8, collar, 64, 10,
              squash=0.7)


kit.pieced("orange_saw", orange_saw_whole, (48, 56), kit.grid_pieces("orange_saw_", SAW, ["tl", "tr", "bl", "br"], 2, 2))


# --- ' 169: the berry in the ring -----------------------------------------------------------------------

RING = kit.frame("BUG", 24, (12, 14))
kit.PROTECT += ["berry", "orange"]


@kit.model("berry_ring", mask=lambda: RING.mask())
def berry_ring():
    f = RING
    grey = Painter("bring", shades={0: (3, 4, 5, 6, 7, 8, 9, 0xb, 0xc)}, metallic=0.3, roughness=0.35)
    # The ring: a rounded octagon (as the sprite's outline) round an opening where the berry sits; a thick
    # bevelled band, its outer edge rounded.
    outer = [kit.superellipse(0.0, 0.3, 11.7, 11.9, 2.1, 64)]
    hole = [kit.superellipse(0.4, 0.4, 5.7, 5.5, 2.3, 48)]
    band = kit.relief("ring_band", outer + hole, grey(0x06), sh.pillow_profile(3.0, 2.4, crown=0.5), bottom=0.3,
                      base=0.6, rim=0.5, spacing=0.6)
    kit.paint_sprite(band, f, grey, wall_steps=-1, keep=lambda val: val >> 4 == 0, default=grey(0x05), blur=1,
                     under=grey(0x03), shade_shift=1.0)
    # The dish inside the ring, dark, under the berry.
    dish = pal("bring_dish", 0x03, metallic=0.3, roughness=0.5)
    w.sphere("ring_dish", (0.4, 0.4, 1.4), (6.2, 6.0, 1.4), dish, 32, 10)
    # The twin berry: two glossy red lobes, the right one a little higher, a seam between them.
    red = Painter("berry", shades={7: (1, 2, 3, 4, 5, 6, 7, 9, 0xa)}, metallic=0.1, roughness=0.18, remap={0x4d: 0x76})
    for name, (x, y), (rx, ry, rz) in (("berry_l", (-2.3, 0.2), (4.5, 5.7, 4.2)), ("berry_r", (3.0, 0.8), (4.4, 5.9, 4.6))):
        lobe = w.sphere(name, (x, y, 2.8), (rx, ry, rz), red(0x74), 32, 16)
        kit.paint_sprite(lobe, f, red, wall_steps=-1, keep=lambda val: val >> 4 in (7, 4), default=red(0x73), blur=2,
                         probe=-0.8)
    shine = pal("berry_shine", 0x4d, metallic=0.0, roughness=0.15)
    at, nrm = kit.ellipsoid_point((3.0, 0.8, 2.8), (4.4, 5.9, 4.6), 4.6, 2.4)
    kit.lens("berry_shine", at, nrm, (0.9, 0.7, 0.3), shine, sink=0.15, segments=12)
    # Four gold prongs from the ring's inner edge over the berry's corners.
    gold = pal("bring_prong", 0x79, metallic=0.7, roughness=0.3, glow=0.25)
    for sx, sy in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
        base = Vector((0.4 + sx * 6.2, 0.4 + sy * 6.0, 3.8))
        tip = Vector((0.4 + sx * 4.3, 0.4 + sy * 4.3, 5.4))
        kit.limb(f"prong_{sx}_{sy}", [tuple(base), tuple((base + tip) / 2 + Vector((0, 0, 0.9))), tuple(tip)],
                 [0.75, 0.55, 0.2], gold, segments=8)


# --- ' 130 132: the grape wing ------------------------------------------------------------------------

GRAPES = kit.frame("GRAPES", 48, (24, 14))


def grape_spots(f):
    """The grapes the sprite draws (each a 4 x 4 ball with its highlight, index 0x5e, right of its middle):
    their centres (x, y), the pod's highlights in the middle left out."""
    out = []
    for r, row in enumerate(f.g):
        for c, val in enumerate(row):
            if val == 0x5e and not (21 <= c <= 26 and 9 <= r <= 15) and 3 <= c <= 44:
                out.append((c - f.ox, f.oy - (r + 1)))
    return out


def grape_wing_whole():
    f = GRAPES
    dark = Painter("gwing", shades={5: (0, 2, 3, 4, 5, 6, 8, 0xa, 0xb, 0xc)}, metallic=0.35, roughness=0.22)
    # The wing: a dark blade across the whole sprite, arched (its tips lower), thicker in the middle.
    wing_poly = [(-24.0, 0.2), (-20.5, 0.0), (20.5, 0.0), (24.0, 0.2), (24.0, 9.4), (22.8, 10.0), (-22.8, 10.0),
                 (-24.0, 9.4)]
    wing = kit.relief("gwing", [wing_poly], dark(0x54), sh.pillow_profile(1.4, 1.6, crown=0.5), bottom=0.7, base=5.0,
                      rim=0.4, spacing=0.5)
    kit.displace_z(wing, lambda x, y, z: -2.6 * (x / 24.0) ** 2)
    kit.paint_sprite(wing, f, dark, wall_steps=-2, keep=lambda val: val >> 4 == 5, default=dark(0x53), blur=1,
                     under=dark(0x50))
    # The spurs at its tips: pale spikes pointing down the screen.
    spur = pal("gwing_spur", 0x5c, metallic=0.4, roughness=0.3)
    for x in (-22.6, 22.6):
        kit.limb(f"gwing_spur{x:+.0f}", [(x, 10.4, 3.4), (x, 4.0, 3.0), (x, -1.5, 2.6), (x * 1.01, -6.0, 2.4)],
                 [0.9, 0.85, 0.6, 0.12], spur, segments=8)
    # The glossy pod in the middle of the bunch.
    pod_mats = Painter("gpod", shades={5: (5, 7, 0xa, 0xb, 0xc, 0xe), 7: (0xf,)}, metallic=0.2, roughness=0.15,
                       remap={0x7f: 0x5e})
    pod = w.sphere("gpod", (0.0, 3.4, 8.0), (3.9, 6.6, 4.8), pod_mats(0x57), 32, 18)
    for vt in pod.data.vertices:  # a teardrop, narrower towards its top
        vt.co.x *= 1.0 - 0.38 * kit.smoothstep(-1.0, 6.6, vt.co.y - 3.4)
    kit.paint_sprite(pod, f, pod_mats, wall_steps=-1, keep=lambda val: val >> 4 in (5, 7), default=pod_mats(0x55),
                     blur=1)
    glint = pal("gpod_glint", 0x7f, metallic=0.0, roughness=0.1, glow=0.6)
    at, nrm = kit.ellipsoid_point((0.0, 3.4, 8.0), (3.9, 6.6, 4.8), 0.0, 1.4)
    kit.lens("gpod_glint", at, nrm, (0.7, 0.9, 0.25), glint, sink=0.12, segments=12)
    # The grapes: a dome of pale berries round the pod, two curled strings of them hanging below.
    berries = [pal("grape_b", 0x5b, metallic=0.15, roughness=0.25), pal("grape_c", 0x5c, metallic=0.15, roughness=0.25)]
    stalk = pal("grape_stalk", 0x56, metallic=0.2, roughness=0.5)
    grapes = []
    for i, (x, y) in enumerate(grape_spots(f)):
        if y < -7.0:  # the hanging strings
            z = 4.2
        else:
            d = math.hypot(x / 12.0, (y - 3.0) / 11.0)
            z = 5.0 + 4.0 * max(0.0, 1.0 - d * d)
        grapes.append(w.sphere(f"grape{i}", (x, y, z), (2.5, 2.5, 2.3), berries[i % 2], 16, 8))
    # A few more behind them, filling the bunch out.
    for i, (x, y) in enumerate(((-3.0, 8.0), (3.0, 8.0), (-3.5, -2.5), (3.5, -2.5), (-7.5, 3.0), (7.5, 3.0))):
        grapes.append(w.sphere(f"grape_back{i}", (x, y, 4.6), (2.5, 2.5, 2.3), berries[(i + 1) % 2], 12, 6))
    kit.join(grapes, "grapes")
    # The stalks of the hanging strings: from the bunch's lowest grapes through theirs, hooking inwards.
    for side in (-1, 1):
        path = [(side * 4.5, -3.0, 6.0), (side * 6.5, -5.5, 5.2), (side * 7.0, -9.0, 4.2), (side * 4.0, -12.0, 4.2)]
        kit.limb(f"grape_stalk{side:+d}", path, [0.5] * len(path), stalk, segments=6)


kit.PROTECT += ["gpod"]
kit.pieced("grape_wing", grape_wing_whole, (48, 28), kit.grid_pieces("grape_wing_", GRAPES, ["l", "r"], 2, 1))


if __name__ == "__main__":
    kit.run()
