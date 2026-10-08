"""Batch AD of wave 3 (sheet H), TORM's beetle, modelled as the sprites look (models.cfg: yaw=0); the kit is
wave3_ad_kit.py, the pixels wave3_ad_art.py.

- torm_beetle_tip, torm_beetle_seg1_l, _seg1_r, torm_beetle_seg2_l, _seg2_r, torm_beetle_tl, _tm, _tr,
  torm_beetle_bl, _bm, _br (H 155; 192, 194; 230, 232; 159, 161, 163 above 197, 199, 201): the beetle TORM's
  custom events put together on the top layer, its head down the screen: from 199 at (x, y), 155 at
  (x, y - 80), 192 and 194 at (x -+ 12, y - 60), 230 and 232 at (x -+ 12, y - 40), 159, 161, 163 at
  (x - 24 .. x + 24, y - 24) and 197, 199, 201 at (x - 24 .. x + 24, y), each event drawn over the ones
  before it. A ribbed grey spike at its tail, two segments of a grey collar plate with bulging shoulders
  under a green shell (the second bigger, its shell ribbed), and its body: a grey thorax with a pale
  ring on its back, green bulbs at its sides, a head with two glowing red eyes, a green nose and green
  mouth claws, tapering to a snout, two long sickle legs curving round from its shoulders and two thin
  feelers. The segments are links of their own, which the events move after the head (they follow it like
  a tail), so each segment is whole in its own pieces and tucks under the next; the body is cut into its
  six sprites (origin). Built in the whole beetle's coordinates (72 x 108, its centre the origin).

usage: Blender -b --factory-startup -P wave3_ad_torm.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ad_kit as kit  # noqa: E402
from wave3_ad_kit import art, k, sh, w, pal, Frame, Painter  # noqa: E402

OUTLINE = {0x01, 0x60, 0x61}
WHOLE = Frame(art.TORM, 72, (36, 54))
TIP = Frame(art.TORM_TIP, 24, (12, 54))
SEG1 = Frame(art.TORM_SEG1, 48, (24, 34))
SEG2 = Frame(art.TORM_SEG2, 48, (24, 14))
BODY = Frame(art.TORM_BODY, 72, (36, -2))
AX = 0.5  # the beetle's axis of symmetry (the middle of pixel column 36)


def mirror(x):
    return 2 * AX - x


def painter(prefix, dark=0x61):
    return Painter(prefix, shades={6: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd, 0xe),
                                   2: (2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc), 0: (2, 3)},
                   metallic=0.25, roughness=0.38, finish={2: (0.15, 0.32)},
                   remap={0x01: dark, 0x00: dark, 0x60: max(0x60, dark), 0x61: max(0x61, dark)})


def lum_relief(f, scale, lo=-1.5, hi=1.8, fade_height=2.5):
    """z_fn for kit.relief: the top raised where the sprite is light, sunk where it is dark (its creases),
    fading out towards the outline."""
    light = w.sampler(f.g, (f.ox, f.oy), value=kit.luminance, blur=1, keep=lambda v: v is not None)
    mean = sum(kit.luminance(v) for row in f.g for v in row if v is not None) / \
        max(1, sum(1 for row in f.g for v in row if v is not None))

    def shape(x, y, z):
        r = max(lo, min(hi, (light(x, y) - mean) * scale))
        fade = min(1.0, max(0.0, z / fade_height))
        return max(0.2, z + r * fade)
    return shape


def segment(prefix, f, plate_height, shell_base, shell_height, ribs, plate_spacing, shell_spacing):
    """A segment: the grey collar plate (the sprite's whole outline), the green shell on it."""
    paint = painter(prefix, dark=0x64)
    pf = Frame(art.TORM_SEG1 if f is SEG1 else art.TORM_SEG2, 48, (f.ox, f.oy)).fill(OUTLINE)
    polys = kit.outlines_of(f, lambda v, c, r: v is not None, smooth=2, epsilon=0.35, min_area=3.0)
    plate = kit.relief(prefix + "_plate", polys, paint(0x68),
                       sh.round_profile(0.8, max_height=plate_height), bottom=0.0, base=0.0,
                       z_fn=lum_relief(f, 7.0), spacing=plate_spacing, angle=45)
    kit.paint_sprite(plate, pf, paint, wall_steps=-1, blur=1, probe=-0.8, default=paint(0x66),
                     keep=lambda v: v >> 4 != 2, shade_shift=0.6)
    kit.paint_sprite(plate, pf, paint, wall_steps=-1, blur=1, probe=-0.8, default=None,
                     keep=lambda v: v >> 4 == 2, ramp_of=lambda v: 6, shade_shift=-0.5)
    green = kit.outlines_of(f, lambda v, c, r: v is not None and v >> 4 == 2, grow=0.3, smooth=2, epsilon=0.35,
                            min_area=6.0)
    shell = kit.relief(prefix + "_shell", green, paint(0x26),
                       sh.round_profile(0.75, max_height=shell_height), bottom=0.0, base=shell_base,
                       z_fn=lum_relief(f, ribs, lo=-0.8, hi=1.2, fade_height=shell_base + 1.5), spacing=shell_spacing,
                       angle=45)
    kit.paint_sprite(shell, pf, paint, wall_steps=-1, blur=1, probe=-0.6, default=paint(0x24),
                     ramp_of=lambda v: 2, shade_shift=0.8)


def tip():
    paint = painter("tip")
    pf = Frame(art.TORM_TIP, 24, (TIP.ox, TIP.oy)).fill(OUTLINE)
    polys = kit.outlines_of(TIP, lambda v, c, r: v is not None, smooth=2, epsilon=0.3, min_area=3.0)
    spike = kit.relief("tip_spike", polys, paint(0x68), sh.round_profile(0.95, max_height=10.0), bottom=0.0,
                       base=0.0, z_fn=lum_relief(TIP, 8.0, lo=-1.2, hi=1.4), spacing=0.65, angle=40)
    kit.paint_sprite(spike, pf, paint, wall_steps=-1, blur=1, probe=-0.6, default=paint(0x66), shade_shift=0.5)


def beetle_body():
    """The thorax, head and snout, the ring on its back, its eyes, bulbs, claws, legs and feelers."""
    f = BODY
    wf = Frame(art.TORM, 72, (36, 54)).fill(OUTLINE)
    paint = painter("sp")
    X, Y = WHOLE.X, WHOLE.Y

    # The core: thorax, head and snout, an outline traced round the sprite's body (left side, mirrored).
    left = [(33.5, 63.3), (29.0, 63.6), (26.4, 64.6), (25.6, 66.0), (26.6, 68.0), (27.2, 72.0), (27.0, 76.5),
            (26.4, 79.5), (27.0, 82.5), (28.4, 86.0), (30.0, 89.5), (31.3, 93.0), (32.2, 97.0), (33.2, 100.5),
            (34.6, 103.8), (36.0, 106.4)]
    pts = [(X(c - 0.5), Y(r - 0.5)) for c, r in left]
    poly = pts + [(mirror(x), y) for x, y in reversed(pts[:-1])]
    poly = [(x, y) for x, y in poly]
    if sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
           for i in range(len(poly))) < 0:
        poly = poly[::-1]
    whole_light = lum_relief(WHOLE, 6.0, lo=-1.4, hi=1.6, fade_height=3.0)

    def core_z(x, y, z):
        # Lower towards the snout, the thorax the highest.
        dy = y - Y(73.5)
        dome = 1.0 + 0.18 * math.exp(-(dy / 9.0) ** 2)
        return whole_light(x, y, z * dome)
    core = kit.relief("sp_core", [poly], paint(0x68), sh.round_profile(1.25, max_height=13.5), bottom=0.0,
                      base=0.0, z_fn=core_z, spacing=0.65, angle=42)
    kit.paint_sprite(core, wf, paint, wall_steps=-1, blur=1, probe=-0.7, default=paint(0x66), shade_shift=0.7)

    # The pale ring on its back round a darker boss.
    cx, cy = X(36.0), Y(73.0)
    top = sh.surface_z(core, cx, cy, 13.0)
    ring = pal("sp_ring", 0x6c, metallic=0.55, roughness=0.25)
    ring_light = pal("sp_ring_light", 0x6e, metallic=0.55, roughness=0.2)
    boss = pal("sp_boss", 0x69, metallic=0.5, roughness=0.3)
    hoop = kit.hoop("sp_ring", (cx, cy, top - 0.9), [(4.3 + 1.1 * math.cos(a), 0.9 * math.sin(a))
                                               for a in [2 * math.pi * i / 10 for i in range(10)]], ring, segments=40)
    w.paint_faces(hoop, lambda c, nrm: ring_light if nrm.z > 0.4 and (c.x - cx) + (c.y - cy) < 1.5
                  else None)
    w.sphere("sp_boss", (cx, cy, top - 0.6), (3.4, 3.4, 1.4), boss, 24, 10)

    # The eyes: red lenses glowing in the head's front.
    eye = pal("sp_eye", 0x77, metallic=0.0, roughness=0.25, glow=2.2)
    eye_hot = pal("sp_eye_hot", 0x7a, metallic=0.0, roughness=0.2, glow=2.8)
    for side in (-1, 1):
        ex, ey = X(29.6), Y(81.2)
        if side > 0:
            ex = mirror(ex)
        ez = sh.surface_z(core, ex, ey, 8.0)
        kit.lens(f"sp_eye{side}", (ex, ey, ez), (0.25 * side, -0.35, 1.0), (1.6, 1.0, 0.6), eye, sink=0.25, segments=18)
        kit.lens(f"sp_eye_hot{side}", (ex + 0.15 * side, ey - 0.1, ez + 0.1), (0.25 * side, -0.35, 1.0),
                 (0.7, 0.45, 0.4), eye_hot, sink=0.1, segments=12)

    # The green bulbs at the thorax's sides.
    bulb = Painter("sp_bulb", shades={2: (3, 4, 5, 6, 7, 8, 9, 0xb, 0xd)}, metallic=0.3, roughness=0.28)
    for side in (-1, 1):
        bx, by = X(26.8), Y(73.0)
        if side > 0:
            bx = mirror(bx)
        b = w.sphere(f"sp_bulb{side}", (bx, by, 5.2), (3.0, 5.2, 4.6), bulb(0x26), 20, 10)
        kit.paint_sprite(b, wf, bulb, wall_steps=-2, blur=1, default=bulb(0x24), ramp_of=lambda v: 2)

    # The green mouth claws beside the head: two small curved hooks a side.
    claw = Painter("sp_claw", shades={2: (3, 4, 5, 6, 7, 8, 9, 0xa)}, metallic=0.3, roughness=0.3)
    for side in (-1, 1):
        for name, path, rad in (("outer", [(25.0, 81.0, 4.5), (23.0, 83.5, 4.0), (21.6, 86.5, 3.4), (20.8, 90.5, 2.6)],
                                 (1.0, 0.85, 0.6, 0.3)),
                                ("inner", [(27.5, 84.0, 4.2), (26.2, 86.8, 3.8), (25.4, 89.5, 3.2), (25.0, 92.0, 2.6)],
                                 (0.95, 0.8, 0.55, 0.3))):
            pts3 = [(X(c - 0.5), Y(r - 0.5), z) for c, r, z in path]
            if side > 0:
                pts3 = [(mirror(x), y, z) for x, y, z in pts3]
            dense = w.catmull(pts3, 0.4)
            radii = [rad[min(len(rad) - 1, int(i / max(1, len(dense) - 1) * (len(rad) - 1) + 0.5))] for i in range(len(dense))]
            c = kit.loft_path(f"sp_claw_{name}{side}", dense, radii, claw(0x26), segments=10, squash=0.8)
            kit.paint_sprite(c, wf, claw, wall_steps=-2, blur=1, default=claw(0x25), ramp_of=lambda v: 2)

    # The sickle legs: from the shoulders up and out, round and down to points level with the snout.
    leg_path = [(25.0, 70.5, 8.5), (21.0, 69.6, 9.0), (16.5, 69.4, 8.8), (12.8, 70.6, 8.2), (10.6, 73.6, 7.4),
                (9.0, 77.0, 6.6), (7.6, 81.0, 5.8), (7.0, 85.0, 5.2), (7.2, 89.0, 4.6), (8.6, 92.6, 4.0),
                (11.0, 95.6, 3.4), (13.8, 97.4, 2.8), (16.2, 98.4, 2.4)]
    leg_radius = [4.0, 4.1, 3.8, 3.3, 2.9, 2.6, 2.4, 2.3, 2.2, 2.0, 1.7, 1.3, 0.7]
    for side in (-1, 1):
        pts3 = [(X(c - 0.5), Y(r - 0.5), z) for c, r, z in leg_path]
        if side > 0:
            pts3 = [(mirror(x), y, z) for x, y, z in pts3]
        dense = w.catmull(pts3, 0.6)
        radii = []
        for q in dense:
            j = min(range(len(pts3)), key=lambda m: (pts3[m][0] - q.x) ** 2 + (pts3[m][1] - q.y) ** 2)
            radii.append(leg_radius[j])
        leg = kit.loft_path(f"sp_leg{side}", dense, [(r, r * 0.8) for r in radii], paint(0x68), segments=12)
        kit.paint_sprite(leg, wf, paint, wall_steps=-1, blur=1, probe=-0.4, default=paint(0x67),
                         ramp_of=lambda v: 6, shade_shift=0.6)

    # Two short horns rising from the thorax's front edge up the screen, towards the shell before it.
    horn_path = [(34.2, 65.0, 10.0), (32.8, 62.0, 10.8), (31.2, 59.4, 10.6), (29.8, 57.2, 9.8)]
    for side in (-1, 1):
        pts3 = [(X(c - 0.5), Y(r - 0.5), z) for c, r, z in horn_path]
        if side > 0:
            pts3 = [(mirror(x), y, z) for x, y, z in pts3]
        dense = w.catmull(pts3, 0.4)
        radii = [1.5 - 0.8 * i / (len(dense) - 1) for i in range(len(dense))]
        horn = kit.loft_path(f"sp_horn{side}", dense, radii, paint(0x68), segments=10)
        kit.paint_sprite(horn, wf, paint, wall_steps=-1, blur=1, default=paint(0x68), ramp_of=lambda v: 6,
                         shade_shift=0.5)

    # The feelers: thin rods from beside the neck out along the segment's edge, hooking down at their ends.
    feeler_path = [(26.0, 61.0, 9.0), (22.0, 60.0, 9.4), (17.0, 59.6, 9.0), (12.5, 59.8, 8.2), (9.8, 61.0, 7.2),
                   (8.6, 62.8, 6.2)]
    for side in (-1, 1):
        pts3 = [(X(c - 0.5), Y(r - 0.5), z) for c, r, z in feeler_path]
        if side > 0:
            pts3 = [(mirror(x), y, z) for x, y, z in pts3]
        dense = w.catmull(pts3, 0.4)
        radii = [1.3 - 0.6 * i / (len(dense) - 1) for i in range(len(dense))]
        fl = kit.loft_path(f"sp_feeler{side}", dense, radii, paint(0x69), segments=8)
        kit.paint_sprite(fl, wf, paint, wall_steps=-1, blur=1, default=paint(0x68), ramp_of=lambda v: 6)


def beetle_whole():
    tip()
    # The segments: the first under the second, the second under the body (each tucks under the next).
    segment("seg1", SEG1, 8.5, 4.6, 6.0, 4.0, 0.8, 0.7)
    segment("seg2", SEG2, 9.5, 5.2, 7.0, 7.0, 0.9, 0.8)
    beetle_body()


SPIDER_TOP = -26.0  # the body's rows meet at the top of 197-201 (drawn over the last rows of 159-163; the eyes below)
BIG = 200.0
PIECES = [
    ("torm_beetle_tip", ["tip"], (-BIG, BIG, -BIG, BIG), (0.0, 40.0), lambda: TIP.mask()),
    ("torm_beetle_seg1_l", ["seg1"], (-BIG, 0.0, -BIG, BIG), (-12.0, 20.0), lambda: SEG1.mask((0, 24, 0, 28))),
    ("torm_beetle_seg1_r", ["seg1"], (0.0, BIG, -BIG, BIG), (12.0, 20.0), lambda: SEG1.mask((24, 48, 0, 28))),
    ("torm_beetle_seg2_l", ["seg2"], (-BIG, 0.0, -BIG, BIG), (-12.0, 0.0), lambda: SEG2.mask((0, 24, 0, 28))),
    ("torm_beetle_seg2_r", ["seg2"], (0.0, BIG, -BIG, BIG), (12.0, 0.0), lambda: SEG2.mask((24, 48, 0, 28))),
    ("torm_beetle_tl", ["sp_"], (-BIG, -12.0, SPIDER_TOP, BIG), (-24.0, -16.0), lambda: BODY.mask((0, 24, 0, 28))),
    ("torm_beetle_tm", ["sp_"], (-12.0, 12.0, SPIDER_TOP, BIG), (0.0, -16.0), lambda: BODY.mask((24, 48, 0, 28))),
    ("torm_beetle_tr", ["sp_"], (12.0, BIG, SPIDER_TOP, BIG), (24.0, -16.0), lambda: BODY.mask((48, 72, 0, 28))),
    ("torm_beetle_bl", ["sp_"], (-BIG, -12.0, -BIG, SPIDER_TOP), (-24.0, -40.0), lambda: BODY.mask((0, 24, 24, 52))),
    ("torm_beetle_bm", ["sp_"], (-12.0, 12.0, -BIG, SPIDER_TOP), (0.0, -40.0), lambda: BODY.mask((24, 48, 24, 52))),
    ("torm_beetle_br", ["sp_"], (12.0, BIG, -BIG, SPIDER_TOP), (24.0, -40.0), lambda: BODY.mask((48, 72, 24, 52))),
]

kit.PROTECT.extend(["sp_core", "seg1_plate", "seg2_plate"])
kit.grouped("torm_beetle", beetle_whole, (72, 108), PIECES)


if __name__ == "__main__":
    kit.run()
