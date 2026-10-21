"""Batch AF of wave 3 (sheet R), the stand-alone models, modelled as their sprites look (models.cfg: yaw=0). The
glass domes are polish_glass_city.py's and polish_purple_dome.py's, IXMUCANE's boss (the rock heaps) in wave3_af_heap.py; the kit is
wave3_af_kit.py, the pixels wave3_af_art.py.

- flying_stone_a (R 171): the small stone flying at the player in ASSASSIN, IXMUCANE and SAWBLADES: an angular
  lump of brown-grey rock (12 x 14), its flat facets in the sprite's shades, a rusty red streak at its top
  left as the sprite draws it.
- flying_stone_b (R 190): its tan twin, longer and lit along its middle.

Both are faceted rocks over the sprite's outline, as deep below as they stand above (they fly).

usage: Blender -b --factory-startup -P wave3_af.py -- [--only names] [--preview <prefix>] [--check 1] [--stats 1]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_af_kit as a  # noqa: E402
from wave3_af_kit import w, sh, pal  # noqa: E402


def flying_stone(f, prefix, ramp, shades, seed, height, red=None, shift=-1.0):
    """A faceted stone over the frame's outline, its facets in the ramp's shades by the sprite's shade under them
    (lighter facing the sun); red: (material, test(x, y)) paints the facets where the sprite draws a red streak."""
    mats = [pal(f"{prefix}_{s_:x}", ramp * 16 + s_, metallic=0.05, roughness=0.8) for s_ in shades]
    rows = w.regions(f.g, lambda v, c, r: "#")
    poly = max(sh.outlines(rows, "#", (f.ox, f.oy), smooth=2, epsilon=0.25), key=len)
    shade = f.shade((ramp,), blur=1)

    def shade_of(c, n):
        s_ = shade(c.x, c.y) + 1.6 * (-0.45 * n.x + 0.35 * n.y + 0.8 * n.z) + shift
        index = min(range(len(shades)), key=lambda i: abs(shades[i] - s_))
        return index if n.z > -0.2 else 0
    rock = w.faceted_rock("stone", poly, height, mats, seed=seed, depth=height * 0.9, shade_of=shade_of,
                          subdivisions=3, dissolve=9.0)
    if red is not None:
        mat, test = red
        a.paint_faces(rock, lambda c, nrm: mat if nrm.z > 0.2 and test(c.x, c.y) else None)
    return rock


STONE_A = a.frame("PEBBLE_A", 12, (6, 7))
STONE_B = a.frame("PEBBLE_B", 12, (6, 7))


@a.model("flying_stone_a", lambda: STONE_A.mask(), size=(12, 14))
def flying_stone_a():
    rust = pal("fsa_rust", 0x43, metallic=0.05, roughness=0.8)
    flying_stone(STONE_A, "fsa", 0xa, (2, 3, 4, 5, 6, 7, 8, 10), 5, 3.6,
                 red=(rust, lambda x, y: abs(y - x - 8.0) < 1.3 and x < -1.6), shift=-1.8)  # its pixels (1, 3), (2, 2), (3, 1)


@a.model("flying_stone_b", lambda: STONE_B.mask(), size=(12, 14))
def flying_stone_b():
    flying_stone(STONE_B, "fsb", 0x1, (3, 4, 5, 6, 7, 8, 9, 10, 11), 9, 3.4)


if __name__ == "__main__":
    a.run()
