"""Items of wave 3, batch AI (the coins sheet's remaining sprites): the HOT DOG, modelled as its sprite looks; the kit
is enemies/wave3_ai_kit.py, the pixels enemies/wave3_ai_art.py. The hot dog keeps still. (The fruit, the rainbow tick
and the asteroid killer: polish_fruit_items.py; SOH JIN's golden key: polish_key_gold.py; the red armour shell:
polish_red_keel_shell.py.)

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
