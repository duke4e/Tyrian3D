"""Armour ingot (the coins sheet's sprites 127, 129 and 131: values 20002, 20004 and 20008, the armour the ship that
comes when the player's armour runs low leaves (enemy 560); 2x2, 24 x 28 pixels, not animated), polished
(2026-10-20; it replaces ingot.py's tipped bar). models.cfg: sprite coins 127/129/131 ingot spin=1.5 color=sprite.

131 is 127 in ramp 3 (blue) instead of ramp 0 (grey), a few shades lighter (its pixels in the same places); 129 is
drawn differently (a brown bar, ramp 10, with grey bands round it, ramp 0). color=sprite gives the grey model the
ramp most of each sprite's pixels are in: 127 grey, 129 brown, 131 blue (so 129 shows as a plain bronze ingot).
The sprites' dark pixels below and right of the bar (palette 0x40 and 0xa1) are its shadow on the ground: left
out (the game draws the model's own shadow).

As the sprite and its 4x upscales draw it: a cast metal bar lying across the screen at a slant (about 16 x 9
pixels), its top a narrow lit strip, its sides sloping, its long side towards the lower right dark.

A cast ingot: a bar with sloping sides and ends (BOTTOM, TOP, HEIGHT), its edges rounded and lighter (bevel); on
its top a stamped mark: a recessed cartouche with a raised shield in it (the armour it brings). Glossy, half
metallic. Palette shades of ramp 0 without emission (polish_item_kit): color=sprite gives them the sprite's ramp.

The bar is centred on the origin (the sprite draws it about 1.5 pixels left of and half a pixel above the sprite's
centre, its long axis 44 degrees from the screen's horizontal: the check turns and moves it so), so that it turns
in place (spin). It is a little wider than the sprite's bar seen from straight above (the sprite draws its lower
right side too).

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the silhouette against
coins.png, its shadow left out), --preview <prefix>, --only <name,...>, --ramp <0-15> (built in that ramp,
written as _r<ramp>).
"""
import math
import os
import sys

from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402

# The bar: half its length and width at the bottom and at the top, its height; its edges' rounding.
BOTTOM = (8.3, 4.8)
TOP = (6.4, 3.0)
HEIGHT = 4.4
ROUND = 0.45
# The stamp: a cartouche (half sizes, corner radius, depth) with a shield in it (half width, top and point
# measured from the cartouche's middle, how far it stands out of the cartouche's floor).
CARTOUCHE = (3.5, 1.75, 0.8, 0.32)
SHIELD = (1.25, 1.25, -1.45, 0.26)
# The sprite's shadow pixels, left out of the check; where the sprite draws the bar's middle.
SHADOW = (0x40, 0xa1)
SPRITE_CENTRE = (-1.4, 0.4)
# For the silhouette check, the bar is turned as the sprite draws it (degrees about Z).
SPRITE_TURN = 44.0

SHADES = {"top": 11, "side": 9, "end": 8, "bottom": 4, "edge": 12, "recess": 8, "emblem": 13}
METAL = dict(metallic=0.5, roughness=0.3)
FINISH = {"edge": dict(metallic=0.5, roughness=0.22), "emblem": dict(metallic=0.5, roughness=0.22),
          "recess": dict(metallic=0.4, roughness=0.45)}


def bar(mats):
    """The bar: a convex solid from its six faces, its edges rounded."""
    (lb, wb), (lt, wt), h = BOTTOM, TOP, HEIGHT
    planes, keys = [], []
    for sign in (1, -1):
        planes.append(kit.general((0.0, sign * h, wb - wt), (0.0, sign * wb, 0.0)))
        keys.append("side")
        planes.append(kit.general((sign * h, 0.0, lb - lt), (sign * lb, 0.0, 0.0)))
        keys.append("end")
    planes += [kit.flat(h), kit.flat(0.0, below=True)]
    keys += ["top", "bottom"]
    obj = kit.solid("ingot", planes, keys, mats)
    kit.drop_parts(obj)
    kit.bevel(obj, ROUND, segments=2, angle=30.0, mat=mats["edge"])
    return kit.weighted(obj, 30.0)


def rounded_rect(hx, hy, r, segments=6):
    pts = []
    for cx, cy, a0 in ((hx - r, hy - r, 0), (-hx + r, hy - r, 90), (-hx + r, -hy + r, 180), (hx - r, -hy + r, 270)):
        for i in range(segments + 1):
            a = math.radians(a0 + 90.0 * i / segments)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def shield_outline(half, top, point, segments=8):
    """A heater shield, counter-clockwise: a flat top, straight sides down to y = 0, curving in to the point
    (point < 0)."""
    pts = [(half, top), (-half, top), (-half, 0.0)]
    for i in range(1, segments):  # the left curve down to the point
        a = math.radians(90.0 * i / segments)
        pts.append((-half * math.cos(a), point * math.sin(a)))
    pts.append((0.0, point))
    for i in range(segments - 1, 0, -1):  # the right curve up from it
        a = math.radians(90.0 * i / segments)
        pts.append((half * math.cos(a), point * math.sin(a)))
    pts.append((half, 0.0))
    return pts


def build():
    opts = kit.options()
    ramp, _ = kit.ramp_of(opts)
    if not kit.wanted(opts, "ingot"):
        return
    k.reset()
    mats = {key: kit.shade(f"ingot_{key}", v, ramp, **FINISH.get(key, METAL)) for key, v in SHADES.items()}
    body = bar(mats)
    hx, hy, r, depth = CARTOUCHE
    cut = kit.prism("cartouche", rounded_rect(hx, hy, r), HEIGHT - depth, HEIGHT + 1.0, mats["recess"])
    kit.boolean(body, [cut], "DIFFERENCE")
    half, top, point, rise = SHIELD
    emblem = kit.prism("shield", shield_outline(half, top, point), HEIGHT - depth - 0.1, HEIGHT - depth + rise,
                       mats["emblem"])
    kit.bevel(emblem, 0.1, segments=1, angle=30.0)
    kit.flat_shade(emblem)
    parts = [body, emblem]
    # Centred in height (the game centres it anyway).
    kit.transform(parts, Matrix.Translation((0.0, 0.0, -HEIGHT / 2)))
    kit.finish(opts, "ingot", parts, 127, large=True, label="ingot turned %g degrees (coins 127, its shadow left out)"
               % SPRITE_TURN, skip=SHADOW, distance=0.8, shift=SPRITE_CENTRE, turn=SPRITE_TURN)


if __name__ == "__main__":
    build()
