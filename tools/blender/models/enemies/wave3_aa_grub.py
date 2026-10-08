"""Enemies of wave 3, batch AA (sheet E), continued (wave3_aa.py has the round ones, wave3_aa_rocks.py the
boulders in the pit): STARGATE's and ASTEROIDS' lava grubs, modelled as the sprites look (models.cfg: yaw=0).

- lava_grub_l_t1 .. lava_grub_l_t4 above lava_grub_l_b1 .. lava_grub_l_b4 (E 77, 79, 81, 83 above 115, 117,
  119, 121; events 662-669 and 1122-1129 at (x + 24 i, y) above (x + 24 i, y + 28), on the ground): the
  grub with its head to the left, crawling in from the right: a long body of red-hot armour plates with
  glowing seams between them, pale knobs along its back, a crested head with two white-hot eyes over an
  open jaw, a curled hook of a tail, a long sickle claw under its head and a shorter one under its middle.
  The body is a relief inflated from the sprite's outline, its plates and seams raised and sunk by the
  sprite's light and dark, painted with its colours (the brightest glow); eyes, knobs and claws are parts
  of their own. Built whole and cut into its eight sprites (origin).
- lava_grub_r_t1 .. lava_grub_r_t4 above lava_grub_r_b1 .. lava_grub_r_b4 (E 85, 87, 89, 91 above 123, 125,
  127, 129; events 670-677 and 1130-1137): its mirror image, its head to the right, crawling in from the
  left (the sheet draws it one pixel to the left of the exact mirror).

usage: Blender -b --factory-startup -P wave3_aa_grub.py -- [--only name,name] [--preview <prefix>]
       [--check 1] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_aa_kit as kit  # noqa: E402
from wave3_aa_kit import art, k, sh, w, pal, Frame, Painter  # noqa: E402

GRUB = Frame(art.GRUB, 96, (48, 28))
GRUB_B = Frame(art.GRUB_B, 96, (48, 28))

# The claws, along the sprite's pixels (continuous column, row; radius; height above the ground).
CLAW_FRONT = [((10.2, 39.4), 0.7, 1.4), ((11.6, 42.4), 1.3, 1.6), ((13.8, 45.2), 1.8, 1.9), ((17.0, 47.6), 2.1, 2.1),
              ((21.5, 49.3), 2.3, 2.2), ((27.0, 50.0), 2.4, 2.3), ((32.5, 49.6), 2.4, 2.5), ((37.5, 48.4), 2.4, 2.9),
              ((41.5, 46.6), 2.4, 3.4), ((44.0, 44.0), 2.4, 4.2)]
CLAW_MID = [((45.6, 48.0), 0.7, 1.4), ((48.5, 48.6), 1.4, 1.7), ((52.5, 48.6), 1.9, 2.0), ((56.5, 47.6), 2.1, 2.3),
            ((60.0, 46.2), 2.2, 2.8), ((63.0, 44.2), 2.2, 3.6), ((65.0, 42.0), 2.2, 4.5)]
# The eyes: (column, row) of their middles, radii (x, y).
EYES = [((23.8, 14.6), (3.7, 2.0)), ((23.4, 21.2), (3.9, 2.2))]
BODY_HEIGHT = 14.0


def is_claw(c, r):
    """The claws' pixels: the front one under the head and along the bottom, the middle one under the body."""
    if r >= 38 and c <= 24:
        return True
    if r >= 47 and c <= 44:
        return True
    if r >= 47 and 45 <= c <= 62:
        return True
    if r == 46 and 45 <= c <= 53:
        return True
    return False


def luminance(v):
    r, g, b = k.level_palette()[v]
    return (0.3 * r + 0.59 * g + 0.11 * b) / 255.0


def grub_whole():
    f = GRUB
    g = f.g
    painter = Painter("grub", shades={4: (1, 3, 5, 7, 9, 0xb), 7: (1, 2, 3, 4, 5, 6, 7, 8, 9, 0xa, 0xb, 0xc, 0xe),
                                      0xa: (3, 5, 7, 9, 0xb)},
                      metallic=0.15, roughness=0.38,
                      glow={0x78: 0.25, 0x79: 0.45, 0x7a: 0.7, 0x7b: 1.0, 0x7c: 1.3, 0x7e: 1.8},
                      finish={4: (0.2, 0.35), 0xa: (0.15, 0.4)})
    # The light of the sprite, smoothed: its dark seams and recesses sink, its lit plates stand out.
    light = w.sampler(g, (f.ox, f.oy), value=lambda v: luminance(v), blur=1, keep=lambda v: v is not None)

    # The body: the sprite's outline but the claws, inflated round, as high as BODY_HEIGHT along its back.
    polys = kit.outlines_of(f, lambda v, c, r: v is not None and not is_claw(c, r), smooth=2, epsilon=0.35,
                            min_area=4.0)

    def shape(x, y, z):
        lum = light(x, y)
        relief = (lum - 0.2) * 12.0
        relief = max(-3.4, min(2.0, relief))
        # The relief fades towards the outline, so the edges stay where the sprite puts them.
        fade = min(1.0, max(0.0, (z - 0.4) / 3.0))
        return max(0.3, z + relief * fade)
    body = kit.relief("grub_body", polys, painter(0x74), sh.round_profile(0.85, max_height=BODY_HEIGHT), bottom=0.0,
                      base=0.0, z_fn=shape, spacing=0.7, angle=45)
    kit.paint_sprite(body, f, painter, wall_steps=-2, blur=1, probe=-0.8, default=painter(0x73), shade_shift=0.8)

    # The eyes: white-hot slits set into the head.
    hot = pal("grub_eye", 0x7f, metallic=0.0, roughness=0.2, glow=2.4)
    warm = pal("grub_eye_rim", 0x7a, metallic=0.0, roughness=0.25, glow=1.2)
    for i, ((c, r), (ex, ey)) in enumerate(EYES):
        x, y = f.X(c - 0.5), f.Y(r - 0.5)
        z = sh.surface_z(body, x, y, 6.0)
        kit.lens(f"grub_eye_rim{i}", (x, y, z), (0, 0, 1), (ex + 0.45, ey + 0.4, 0.8), warm, sink=0.45)
        kit.lens(f"grub_eye{i}", (x, y, z), (0, 0, 1), (ex, ey, 0.8), hot, sink=0.3)

    # The knobs along its back: pale pink bumps where the sprite draws its light pink (ramp 4) spots; the
    # tail's hook and the spots on the claws stay painted.
    pale = Painter("grub_knob", shades={4: (5, 7, 9, 0xb)}, metallic=0.15, roughness=0.4)
    spots = kit.blobs(g, lambda v: v is not None and v >> 4 == 4 and (v & 15) >= 6, min_size=6)
    for i, (c, r, size, index) in enumerate(spots):
        x, y = f.X(c - 0.5), f.Y(r - 0.5)
        if size > 40 or r > 38:
            continue
        rad = min(2.3, 0.5 + 0.42 * math.sqrt(size))
        z = sh.surface_z(body, x, y, 4.0)
        w.sphere(f"grub_knob{i}", (x, y, z - rad * 0.5), (rad, rad * 0.9, rad * 0.7), pale(index - 3), 16, 8)

    # The claws: tapering curved tubes on the ground, painted by the sprite.
    for name, path in (("front", CLAW_FRONT), ("mid", CLAW_MID)):
        pts = [(f.X(c - 0.5), f.Y(r - 0.5), z) for (c, r), _, z in path]
        radii = [rad for _, rad, _ in path]
        dense = w.catmull(pts, 0.5)
        # Radii along the dense path, by nearest control point.
        rr = []
        for q in dense:
            j = min(range(len(pts)), key=lambda m: (pts[m][0] - q.x) ** 2 + (pts[m][1] - q.y) ** 2)
            rr.append(radii[j])
        claw = w.tube("grub_claw_" + name, dense, rr, painter(0x75), 12, squash=0.75)
        kit.paint_sprite(claw, f, painter, wall_steps=-2, blur=1, default=painter(0x74))


def grub_mirror_whole():
    """The mirror image: the grub built, mirrored, moved a pixel to the right (as the sheet draws it)."""
    grub_whole()
    kit.bake()
    kit.mirror_scene(0.0)
    sh.move(kit.meshes(), 1.0, 0.0)


kit.PROTECT.append("grub_body")
kit.pieced("lava_grub_l", grub_whole, (96, 56),
           kit.grid_pieces("lava_grub_l_", GRUB, ["t1", "t2", "t3", "t4", "b1", "b2", "b3", "b4"], 4, 2))
kit.pieced("lava_grub_r", grub_mirror_whole, (96, 56),
           kit.grid_pieces("lava_grub_r_", GRUB_B, ["t1", "t2", "t3", "t4", "b1", "b2", "b3", "b4"], 4, 2))


if __name__ == "__main__":
    kit.run()
