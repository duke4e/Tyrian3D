"""Items of wave 3, batch AI (the coins sheet's remaining sprites): the red armour shell and the HOT DOG, modelled as
their sprites look; the kit is enemies/wave3_ai_kit.py, the pixels enemies/wave3_ai_art.py. The hot dog keeps still.
(The fruit, the rainbow tick and the asteroid killer: polish_fruit_items.py; SOH JIN's golden key: polish_key_gold.py.)

usage: Blender -b --factory-startup -P wave3_ai_items.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "enemies"))
import wave3_ai_kit as kit  # noqa: E402
from wave3_ai_kit import k, sh, w, pal, Painter  # noqa: E402


# --- Coins 279: the red armour shell ----------------------------------------------------------------------------

RED_PLATE = kit.frame("RED_PLATE", 24, (12, 14))


@kit.model("red_keel_shell", mask=lambda: RED_PLATE.mask())
def red_keel_shell():
    """Enemy 560 (100 credits, armour 5): a red shell shaped like a T, a thick rolled bar across its top over a
    gold rod, a grooved keel running down to a blunt point, and two ribbed gold pods either side of the keel
    under the bar. Symmetric about x = 0.5, as the sprite."""
    ax = 0.5
    red = pal("rks_red", 0x47, metallic=0.3, roughness=0.32)
    red_light = pal("rks_red_light", 0x4a, metallic=0.3, roughness=0.28)
    groove = pal("rks_groove", 0x42, metallic=0.2, roughness=0.5)
    gold = pal("rks_gold", 0x17, metallic=0.7, roughness=0.3)
    gold_light = pal("rks_gold_light", 0x1b, metallic=0.7, roughness=0.25)
    # The gold rod behind the bar's top edge.
    w.lathe_axis("rks_rod", [(0.0, 0.01), (0.3, 1.0), (1.0, 1.35), (11.0, 1.35), (11.7, 1.0), (12.0, 0.01)], gold,
                 (ax - 6.0, 12.5, 3.2), (1, 0, 0), segments=16)
    # The rolled bar: a capsule across, a little flattened, its middle fuller.
    bar = w.lathe_axis("rks_bar", [(0.0, 0.01), (0.25, 1.6), (0.9, 2.7), (2.0, 3.3), (5.0, 3.5), (11.0, 3.7),
                                   (17.0, 3.5), (20.0, 3.3), (21.1, 2.7), (21.75, 1.6), (22.0, 0.01)], red,
                       (ax - 11.0, 8.7, 3.4), (1, 0, 0), segments=28, squash=0.95)
    # The bar's top lighter, as the sprite shades it.
    kit.paint_faces(bar, lambda c, nrm: red_light if nrm.z > 0.75 else None)
    # The keel: from under the bar down to its blunt point, round on top with a groove down its middle.
    sections = [(6.5, 4.4, 4.0), (3.0, 4.6, 4.4), (-1.0, 4.6, 4.2), (-5.0, 4.4, 3.8), (-8.0, 3.9, 3.3),
                (-10.5, 2.9, 2.6), (-12.5, 1.7, 1.8), (-13.6, 0.4, 0.8)]
    pts = k.profile([(yy, hw, hh) for yy, hw, hh in reversed(sections)], step=0.5)
    rings = [k.ring(yy, hw, hh, 28, x=ax, z=0.4, power=2.3, bottom=0.25) for yy, hw, hh in pts]
    keel = k.loft("rks_keel", rings, red)
    k.smooth(keel, 55)
    kit.limb("rks_groove", [(ax, 5.0, 4.45), (ax, 0.0, 4.55), (ax, -5.0, 4.15), (ax, -9.5, 3.0), (ax, -12.6, 1.8)],
             [0.38, 0.4, 0.38, 0.32, 0.2], groove, segments=8, squash=0.5)
    # The gold pods: ribbed, rounded, either side of the keel.
    for side in (-1, 1):
        cx = ax + side * 6.6
        pod = w.sphere(f"rks_pod{side:+d}", (cx, -0.6, 2.4), (2.4, 7.4, 2.6), gold, 20, 14)
        for vt in pod.data.vertices:  # ribs across it
            vt.co.x += side * 0.18 * math.cos((vt.co.y + 0.6) * 1.9) * max(0.0, vt.co.z - 1.0) / 3.0
        kit.paint_faces(pod, lambda c, nrm: gold_light if nrm.z > 0.8 else None)
        k.smooth(pod, 60)


# --- Coins 92: the HOT DOG pick-up ------------------------------------------------------------------------------

HOTDOG = kit.frame("HOTDOG", 24, (12, 14))
kit.PROTECT += ["hd_letters"]


def plate_ellipse(f):
    """The blue plate's ellipse from its pixels' moments: centre, semi-axes and angle (radians)."""
    pts = [(f.X(c), f.Y(r)) for r, row in enumerate(f.g) for c, val in enumerate(row)
           if val is not None and val >> 4 in (1, 3) or (val is not None and val >> 4 == 7 and 6 <= r <= 20)]
    n_ = len(pts)
    mx, my = sum(p[0] for p in pts) / n_, sum(p[1] for p in pts) / n_
    sxx = sum((p[0] - mx) ** 2 for p in pts) / n_
    syy = sum((p[1] - my) ** 2 for p in pts) / n_
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts) / n_
    angle = 0.5 * math.atan2(2 * sxy, sxx - syy)
    tr, det = sxx + syy, sxx * syy - sxy * sxy
    l1 = tr / 2 + math.sqrt(max(0.0, tr * tr / 4 - det))
    l2 = tr / 2 - math.sqrt(max(0.0, tr * tr / 4 - det))
    return (mx, my), 2 * math.sqrt(l1), 2 * math.sqrt(l2), angle


@kit.model("hot_dog", mask=lambda: HOTDOG.mask())
def hot_dog():
    """The HOT DOG pick-up (it arms the ship with the hot dog weapons): a hot dog in its bun on a blue oval plate,
    the words HOT above and DOG below in raised letters glowing in the sprite's fire shades on dark red backing.
    No spin: the letters stay readable."""
    f = HOTDOG
    blue = pal("hd_plate", 0x39, metallic=0.35, roughness=0.25)
    blue_rim = pal("hd_plate_rim", 0x3c, metallic=0.35, roughness=0.22)
    bun = pal("hd_bun", 0x1a, metallic=0.05, roughness=0.55)
    bun_light = pal("hd_bun_light", 0x1c, metallic=0.05, roughness=0.5)
    sausage = pal("hd_sausage", 0x75, metallic=0.1, roughness=0.3)
    mustard = pal("hd_mustard", 0x7c, metallic=0.05, roughness=0.4, glow=0.2)
    backing = pal("hd_backing", 0x72, metallic=0.2, roughness=0.5, glow=0.2)
    (cx, cy), a, b, angle = plate_ellipse(f)
    a, b = min(a, 12.6), min(b, 7.6)
    # The plate: a shallow dish, its rim raised and rounded.
    prof = [(0.0, 0.01), (0.02, 0.8), (0.35, 0.93), (1.1, 1.0), (1.45, 0.97), (1.4, 0.88), (0.85, 0.8),
            (0.75, 0.5), (0.75, 0.01)]
    plate = w.lathe_axis("hd_plate", prof, blue, (0.0, 0.0, 0.0), (0, 0, 1), segments=40, up=(0, 1, 0))
    plate.data.transform(Matrix.Translation((cx, cy, 0.0)) @ Matrix.Rotation(angle, 4, "Z") @
                         Matrix.Scale(a, 4, (1, 0, 0)) @ Matrix.Scale(b, 4, (0, 1, 0)))
    kit.paint_faces(plate, lambda c, nrm: blue_rim if c.z > 1.2 else None)
    k.smooth(plate, 50)
    # The hot dog across the plate, from its top right to its bottom left (the sprite's bun and sausage).
    top, bottom = Vector((3.2, 7.2, 0.0)), Vector((-4.6, -5.0, 0.0))
    d = (top - bottom).normalized()
    side = Vector((d.y, -d.x, 0.0))  # to the right of the dog (looking along it, up the screen)
    length = (top - bottom).length
    for i, off in enumerate((-1.25, 1.25)):
        start = bottom + side * off + Vector((0, 0, 2.2))
        kit.limb(f"hd_bun{i}", [tuple(start), tuple(start + d * length * 0.5 + Vector((0, 0, 0.5))),
                                tuple(start + d * length)], [1.9, 2.2, 1.9], bun if i else bun_light, segments=12,
                 squash=0.8, step=0.8)
    s0 = bottom - d * 1.0 - side * 0.5 + Vector((0, 0, 3.6))
    kit.limb("hd_sausage", [tuple(s0), tuple(s0 + d * (length + 2.0) * 0.5 + Vector((0, 0, 0.5))),
                            tuple(s0 + d * (length + 2.0))], [1.3, 1.45, 1.3], sausage, segments=10, step=0.8)
    zig = []
    for j in range(9):
        t = 0.1 + 0.8 * j / 8
        zig.append(tuple(s0 + d * (length + 2.0) * t + side * (0.55 if j % 2 else -0.55) +
                         Vector((0, 0, 1.45 + 0.5 * math.sin(math.pi * t)))))
    kit.limb("hd_mustard", zig, [0.32] * len(zig), mustard, segments=6)
    # The letters: HOT across the top, DOG across the bottom; the dark outline pixels a backing, the bright
    # ones raised on it.
    def letter(val, c, r):
        return val >> 4 == 7 and (r <= 5 or (r == 6 and c < 6) or r >= 21)
    back = kit.polys_where(f, letter, smooth=1, epsilon=0.2, min_area=0.5)
    plate_back = kit.relief("hd_letters_back", back, backing, sh.pillow_profile(0.8, 0.4), bottom=0.0, base=0.0,
                            rim=0.3, spacing=0.8, flat=True)
    lift = 2.6
    for obj in (plate_back,):
        obj.data.transform(Matrix.Translation((0, 0, lift)))
    bright = kit.polys_where(f, lambda val, c, r: letter(val, c, r) and (val & 15) >= 6, smooth=0, epsilon=0.05,
                             min_area=0.3, grow=0.12)
    fire = Painter("hd_fire", shades={7: (6, 8, 0xa)}, metallic=0.1, roughness=0.4,
                   glow={0x76: 0.6, 0x78: 0.8, 0x7a: 1.0})
    word = kit.relief("hd_letters", bright, fire(0x78), sh.pillow_profile(1.0, 0.35), bottom=0.0, base=lift + 0.6,
                      rim=0.2, spacing=0.5, sigma=0.6)
    kit.paint_sprite(word, f, fire, wall_steps=-2, keep=lambda val: val >> 4 == 7, blur=0)


if __name__ == "__main__":
    kit.run(items=True)
