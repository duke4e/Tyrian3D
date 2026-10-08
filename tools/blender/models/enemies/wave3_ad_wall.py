"""Batch AD of wave 3 (sheet H), GYGES' creatures in their pieces of tube wall, modelled as the sprites look
(models.cfg: yaw=0); the kit is wave3_ad_kit.py, the pixels wave3_ad_art.py. The sprites draw each creature
in a square of the grey-blue tube wall GYGES' middle layer is made of (they move down the screen with it);
the models keep that square as a low slab of tubes (kit.tube_wall) with the creature rising out of it.
Each is built whole and cut into its sprites' pieces (origin).

- gyges_lurker_tl, _tr, _bl, _br (H 5, 7 above 43, 45; enemies 160, 161 at (x, y - 28), (x + 24, y - 28) and
  158, 159 at (x, y), (x + 24, y), in the sky): the hunched one-eyed blue creature crouching in the wall,
  its head up the screen with a red eye glowing in it (its frames 9, 13 ... light the eye up), its round
  back to the right, its limbs reaching down into the dark under it.
- gyges_brood_tl, _tr, _bl, _br (H 81, 83 above 119, 121; enemies 156, 157 above 154, 155): a brood of
  glossy blue sacs heaped in the wall, veins running over them.
- gyges_stalk_cap, gyges_stalk_tl, _tr, _bl, _br (H 79 over 85, 87 above 123, 125; enemies 416 28 pixels
  over 414, 415 above 412, 413, which the events send in one after the other at one speed, on the top layer
  or in the sky): the grey stalk growing out of the wall, its glossy cap (79, above the wall's square) on a
  thick stem that leans up out of a bulbous root lying on the wall, purple fingers gripping the stem and
  purple tips on the root's two lobes. The green balls and the green spike (wave3_ad.py) swing round over
  its cap.

usage: Blender -b --factory-startup -P wave3_ad_wall.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ad_kit as kit  # noqa: E402
from wave3_ad_kit import art, k, sh, w, pal, Frame, Painter  # noqa: E402

BLUE = {3: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd)}


def blue_painter(prefix):
    return Painter(prefix, shades=BLUE, metallic=0.35, roughness=0.22, remap={0x01: 0x31, 0x00: 0x31})


def lum_relief(f, keep, scale, lo=-1.6, hi=2.0, fade=3.0):
    light = w.sampler(f.g, (f.ox, f.oy), value=kit.luminance, blur=1, keep=lambda v: v is not None and keep(v))
    vals = [kit.luminance(v) for row in f.g for v in row if v is not None and keep(v)]
    mean = sum(vals) / max(1, len(vals))

    def shape(x, y, z):
        return max(0.2, z + max(lo, min(hi, (light(x, y) - mean) * scale)) * min(1.0, z / fade))
    return shape


# --- H 5 7 / 43 45: the lurker ---------------------------------------------------------------------------

LURKER = kit.frame("BLUE_A", 48, (24, 28))
LURKER_LIT = kit.frame("BLUE_A_C", 48, (24, 28))


def lurker_whole():
    f = LURKER
    kit.tube_wall("lurker_wall", f, (-24.0, 24.0, -28.0, 28.0), height=2.4, relief=2.0, step=1.0,
                  prefix="lurker_wall")
    paint = blue_painter("lurker")
    pf = kit.frame("BLUE_A", 48, (24, 28)).fill({0x01, 0x00})
    is_body = lambda v: v >> 4 in (3, 7)  # noqa: E731
    polys = kit.outlines_of(f, lambda v, c, r: v is not None and is_body(v), grow=0.3, smooth=2, epsilon=0.35,
                            min_area=4.0)
    body = kit.relief("lurker_body", polys, paint(0x34), sh.round_profile(0.9, max_height=12.0), bottom=0.0,
                      base=1.0, z_fn=lum_relief(f, is_body, 9.0), spacing=0.75, angle=45)
    kit.paint_sprite(body, pf, paint, wall_steps=-2, blur=1, probe=-0.7, default=paint(0x33),
                     ramp_of=lambda v: 3, shade_shift=0.3)
    # The eye: a red lens glowing in the head.
    eye = pal("lurker_eye", 0x74, metallic=0.0, roughness=0.2, glow=1.5)
    hot = pal("lurker_eye_hot", 0x7a, metallic=0.0, roughness=0.2, glow=2.8)
    ex, ey = f.X(22.5), f.Y(15.0)
    ez = sh.surface_z(body, ex, ey, 9.0)
    kit.lens("lurker_eye", (ex, ey, ez), (-0.2, 0.1, 1.0), (2.0, 1.8, 0.8), eye, sink=0.4, segments=24)
    kit.lens("lurker_eye_hot", (ex + 0.3, ey, ez + 0.2), (-0.2, 0.1, 1.0), (0.9, 0.8, 0.5), hot, sink=0.1,
             segments=14)


kit.PROTECT.append("lurker_body")
kit.pieced("gyges_lurker", lurker_whole, (48, 56),
           kit.grid_pieces("gyges_lurker_", LURKER, ["tl", "tr", "bl", "br"], 2, 2))


# --- H 81 83 / 119 121: the brood ------------------------------------------------------------------------

BROOD = kit.frame("BLUE_B", 48, (24, 28))


def brood_whole():
    f = BROOD
    kit.tube_wall("brood_wall", f, (-24.0, 24.0, -28.0, 28.0), height=2.4, relief=2.0, step=1.0,
                  prefix="brood_wall")
    paint = blue_painter("brood")
    pf = kit.frame("BLUE_B", 48, (24, 28)).fill({0x01, 0x00})
    is_body = lambda v: v >> 4 == 3  # noqa: E731
    polys = kit.outlines_of(f, lambda v, c, r: v is not None and is_body(v), grow=0.3, smooth=2, epsilon=0.35,
                            min_area=6.0)
    body = kit.relief("brood_body", polys, paint(0x34), sh.round_profile(0.8, max_height=9.0), bottom=0.0,
                      base=1.0, z_fn=lum_relief(f, is_body, 7.0), spacing=0.95, angle=45)
    kit.paint_sprite(body, pf, paint, wall_steps=-2, blur=1, probe=-0.7, default=paint(0x33),
                     ramp_of=lambda v: 3, shade_shift=0.2)
    # The sacs: glossy swellings where the sprite's blue is lightest.
    sac = Painter("brood_sac", shades=BLUE, metallic=0.35, roughness=0.15)
    spots = kit.blobs(f.g, lambda v: v is not None and v >> 4 == 3 and (v & 15) >= 6, min_size=7)
    for i, (c, r, size, index) in enumerate(spots):
        x, y = f.X(c - 0.5), f.Y(r - 0.5)
        rad = min(6.5, 2.2 + 0.55 * math.sqrt(size))
        z = sh.surface_z(body, x, y, 6.0)
        s = w.sphere(f"brood_sac{i}", (x, y, z - rad * 0.75), (rad, rad * 0.9, rad * 0.7), sac(0x36), 16, 8)
        sh.cut_planes([s], [((0, 0, 0.5), (0, 0, -1))])
        kit.paint_sprite(s, pf, sac, wall_steps=-2, blur=1, default=sac(0x35), ramp_of=lambda v: 3, shade_shift=0.6)


kit.PROTECT.append("brood_body")
kit.pieced("gyges_brood", brood_whole, (48, 56),
           kit.grid_pieces("gyges_brood_", BROOD, ["tl", "tr", "bl", "br"], 2, 2))


# --- H 79 / 85 87 / 123 125: the stalk -------------------------------------------------------------------

STALK = kit.frame("PURPLE", 48, (24, 56))   # the wall's square: rows 28-83, the cap above it


def stalk_whole():
    f = STALK
    kit.tube_wall("stalk_wall", f, (-24.0, 24.0, -28.0, 28.0), height=2.4, relief=2.0, step=1.0,
                  prefix="stalk_wall")
    grey = Painter("stalk", shades={6: (2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf)}, metallic=0.1,
                   roughness=0.25, remap={0x01: 0x62, 0x00: 0x62})
    purple = Painter("stalk_claw", shades={5: (2, 3, 4, 5, 6, 7, 8, 9, 0xa)}, metallic=0.3, roughness=0.25)
    pf = kit.frame("PURPLE", 48, (24, 56)).fill({0x01, 0x00})
    P = lambda c, r: (f.X(c - 0.5), f.Y(r - 0.5))  # noqa: E731

    # The root lying on the wall: two lobes round a bulb.
    root_outline = [(3, 57), (6, 53.5), (11, 52), (14.5, 49.5), (18.5, 48), (24, 49), (28, 51.5), (30, 55.5),
                    (33, 58.5), (38.5, 60), (42.5, 63), (43.5, 67), (41.5, 72), (36.5, 75), (28, 76.5), (20, 76.5),
                    (12, 74.5), (6.5, 71.5), (3, 66.5), (2, 61)]
    poly = [P(c, r) for c, r in root_outline]
    if sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
           for i in range(len(poly))) < 0:
        poly = poly[::-1]
    root = kit.relief("stalk_root", [poly], grey(0x68), sh.round_profile(0.75, max_height=8.0), bottom=0.0,
                      base=1.5, z_fn=lum_relief(f, lambda v: v >> 4 == 6, 5.0, lo=-1.0, hi=1.4), spacing=0.85,
                      angle=45)
    kit.paint_sprite(root, pf, grey, wall_steps=-1, blur=1, probe=-0.6, default=grey(0x66),
                     ramp_of=lambda v: 6, shade_shift=1.0)
    bx, by = P(19.0, 56.5)
    bulb = w.sphere("stalk_bulb", (bx, by, 6.5), (8.0, 7.2, 5.6), grey(0x69), 32, 16)
    kit.paint_sprite(bulb, pf, grey, wall_steps=-1, blur=1, default=grey(0x68), ramp_of=lambda v: 6,
                     shade_shift=0.6)

    # The stem, leaning up out of the root towards its cap.
    stem_pts = [(*P(20.5, 52.0), 8.0), (*P(21.5, 44.0), 11.0), (*P(22.5, 36.0), 13.5), (*P(23.0, 29.0), 15.0)]
    stem_dense = w.catmull(stem_pts, 0.7)
    stem = kit.loft_path("stalk_stem", stem_dense, [(6.6, 4.6)] * len(stem_dense), grey(0x67), segments=18)
    kit.paint_sprite(stem, pf, grey, wall_steps=-1, blur=1, default=grey(0x66), ramp_of=lambda v: 6, shade_shift=0.2)
    # The cap: a glossy dome, lit at its top left.
    cx, cy = P(23.5, 22.0)
    cap = w.sphere("stalk_cap", (cx, cy, 15.0), (11.8, 6.6, 5.6), grey(0x6b), 40, 20)
    kit.paint_sprite(cap, pf, grey, wall_steps=-1, blur=1, probe=-0.6, default=grey(0x6a), ramp_of=lambda v: 6,
                     shade_shift=0.3)

    # The purple fingers gripping the stem and the purple tips of the lobes.
    for i, path in enumerate(([(22.0, 35.5, 18.4), (19.6, 38.5, 17.6), (18.2, 42.0, 15.8), (18.8, 45.0, 14.4)],
                              [(21.0, 44.0, 15.4), (18.4, 46.5, 14.0), (16.8, 49.2, 12.4), (17.6, 51.5, 11.0)])):
        pts3 = [(*P(c, r), z) for c, r, z in path]
        dense = w.catmull(pts3, 0.5)
        radii = [2.0 - 0.9 * j / (len(dense) - 1) for j in range(len(dense))]
        finger = kit.loft_path(f"stalk_finger{i}", dense, radii, purple(0x56), segments=12)
        kit.paint_sprite(finger, pf, purple, wall_steps=-1, blur=1, default=purple(0x56), ramp_of=lambda v: 5,
                         shade_shift=0.5)
    for i, ((c, r), radii, z) in enumerate((((5.0, 57.5), (3.6, 2.6, 2.4), 4.8), ((35.0, 68.5), (3.4, 4.2, 2.8), 5.2))):
        x, y = P(c, r)
        tip = w.sphere(f"stalk_tip{i}", (x, y, z), radii, purple(0x57), 20, 10)
        kit.paint_sprite(tip, pf, purple, wall_steps=-1, blur=1, default=purple(0x57), ramp_of=lambda v: 5,
                         shade_shift=0.6)


kit.PROTECT.append("stalk_root")
kit.pieced("gyges_stalk", stalk_whole, (48, 84),
           [kit.piece("gyges_stalk_cap", STALK, 12, 0)] +
           [kit.piece("gyges_stalk_" + nm, STALK, c, r) for nm, c, r in (("tl", 0, 28), ("tr", 24, 28), ("bl", 0, 56),
                                                                         ("br", 24, 56))])


if __name__ == "__main__":
    kit.run()
