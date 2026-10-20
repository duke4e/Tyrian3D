"""Enemies of wave 3, batch AI (sheet 0): BOTANY's armoured creatures on the ground, modelled as their sprites look
(models.cfg: yaw=0). The kit is wave3_ai_kit.py, the pixels wave3_ai_art.py; GRYPHON's boss is in
wave3_ai_gryphon.py, the coins sheet's items in items/wave3_ai_items.py, BOTANY B's lilac stone in
polish_botany_stone.py.

- botany_beetle (0 229, enemy 821, BOTANY B): a blue beetle with folded wing cases, each with a ridge along it, its
  narrow tail between their lower ends marked with a glowing red chevron, red streaks on the cases' lower edges
  (its frames 231, 233 light them).

usage: Blender -b --factory-startup -P wave3_ai.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ai_kit as kit  # noqa: E402
from wave3_ai_kit import k, sh, w, pal, Painter  # noqa: E402


def steel(prefix):
    """The blue steel of BOTANY's shells (ramp 3), painted by the sprite's shades."""
    return Painter(prefix, shades={3: (3, 5, 7, 9, 0xa, 0xb, 0xc, 0xd, 0xe)}, metallic=0.25,
                   roughness=0.3, remap={0x30: 0x33})


def shade_by_slope(prefix, levels):
    """A painter for paint_faces giving faces the blue steel by how much they face the camera: levels
    [(lowest normal z, index)] ascending; faces looking down the darkest."""
    mats = [(nz, pal(f"{prefix}_{index:02x}", index, metallic=0.25, roughness=0.3)) for nz, index in levels]

    def pick(c, nrm):
        chosen = mats[0][1]
        for nz, mat in mats:
            if nrm.z >= nz:
                chosen = mat
        return chosen
    return pick


# --- 0 229: the beetle --------------------------------------------------------------------------------------

BEETLE = kit.frame("BEETLE", 24, (12, 14))
BEETLE_PAINT = kit.frame("BEETLE", 24, (12, 14)).fill({0x30})


def wing_pixel(side):
    """The pixels of one wing case: left (side -1) of the middle groove, or right; in the lower half only
    outside the tail (the dark lines in pixel columns 9 and 14)."""
    def keep(val, c, r):
        if r <= 16:
            return c <= 11 if side < 0 else c >= 12
        return c <= 9 if side < 0 else c >= 14
    return keep


@kit.model("botany_beetle", mask=lambda: BEETLE.mask())
def botany_beetle():
    f = BEETLE_PAINT
    paint = steel("beetle")
    dark = pal("beetle_dark", 0x33, metallic=0.25, roughness=0.45)
    red = pal("beetle_red", 0x75, metallic=0.1, roughness=0.2, glow=1.1)
    hot = pal("beetle_red_hot", 0x79, metallic=0.0, roughness=0.2, glow=1.6)
    parts = []
    for side in (-1, 1):
        polys = kit.polys_where(f, wing_pixel(side), smooth=2, epsilon=0.3, min_area=2.0, grow=-0.25)
        ridge_x = side * 2.4

        def top(x, y, z, side=side, ridge_x=ridge_x):
            # A ridge along the case (nearer the middle at the top, out towards its tip lower down), the case
            # sloping off to its outer edge.
            rx = ridge_x + side * max(0.0, 2.2 - y * 0.25) * kit.smoothstep(4.0, -6.0, y)
            d = abs(x - rx)
            return z + 1.5 * max(0.0, 1.0 - d / 2.0) ** 2
        wing = kit.relief(f"beetle_wing{side:+d}", polys, dark, sh.round_profile(aspect=0.62, max_height=4.2),
                          bottom=0.0, base=0.0, rim=0.5, spacing=0.4, z_fn=top)
        parts.append(wing)
    # The tail between the cases' lower ends, and the head at the top of the groove.
    tail = kit.limb("beetle_tail", [(0.0, -1.6, 2.4), (0.0, -4.6, 3.4), (0.0, -7.6, 3.0), (0.0, -9.2, 1.8)],
                    [1.6, 1.9, 1.6, 0.8], dark, segments=16, squash=1.0)
    parts.append(tail)
    cases = shade_by_slope("beetle_case", [(-2, 0x33), (0.0, 0x35), (0.4, 0x37), (0.65, 0x39), (0.85, 0x3b),
                                           (0.96, 0x3c)])
    for obj in parts:
        kit.paint_faces(obj, cases)
    # The red marks: a chevron on the tail, a streak down each case's lower inner edge.
    for side in (-1, 1):
        kit.limb(f"beetle_chevron{side:+d}", [(0.0, -6.3, 4.45), (side * 0.9, -5.4, 4.65), (side * 1.6, -4.4, 4.5)],
                 [0.45, 0.45, 0.35], red, segments=8, squash=0.6)
        x = side * 4.6
        kit.limb(f"beetle_streak{side:+d}", [(x - side * 0.2, -5.7, 2.2), (x + side * 0.9, -7.0, 1.7),
                                            (x + side * 1.8, -8.2, 1.2)], [0.45, 0.5, 0.4], red, segments=8,
                 squash=0.7)
    kit.lens("beetle_spot", (0.0, -5.2, 4.75), (0, 0, 1), (0.6, 0.6, 0.3), hot, sink=0.05, segments=10)
    kit.flatten_under(w.meshes())


if __name__ == "__main__":
    kit.run()
