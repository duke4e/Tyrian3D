"""Batch Q of wave 3 (sheet A: SOH JIN), the bronze grille on the ground; modelled as its sprite looks
(models.cfg: yaw=0). (The bronze whorl, A 91: polish_bronze_whorl.py.)

- bronze_grille (A 89): a bronze plate, an elongated hexagon lying on the ground, with three slanting slots
  side by side (the middle one longest) in which red bars glow.

usage: Blender -b --factory-startup -P wave3_q_bronze.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_q_kit as q  # noqa: E402
from wave3_q_kit import art, pal  # noqa: E402

ORIGIN = (12, 14)


def bronze(prefix, lo=2, hi=14):
    return {s: pal(f"{prefix}_bronze{s}", 0x10 | s, metallic=0.6, roughness=0.32) for s in range(lo, hi + 1)}


def segment_distance(x, y, a, b):
    ax, ay = a
    bx, by = b
    ex, ey = bx - ax, by - ay
    t = max(0.0, min(1.0, ((x - ax) * ex + (y - ay) * ey) / max(ex * ex + ey * ey, 1e-9)))
    return math.hypot(x - ax - t * ex, y - ay - t * ey)


# --- A 89: the bronze grille -------------------------------------------------------------------------

# The slots: their ends (x, y) and half widths, from the sprite's red pixels.
GRILLE_SLOTS = [((-1.3, 7.9), (-5.9, 1.6), 1.35), ((2.6, 5.0), (-3.6, -4.9), 1.7), ((3.6, -1.0), (-0.5, -6.6), 1.35)]
GRILLE_H = 3.8


@q.model("bronze_grille", [(89, True)])
def bronze_grille():
    g = q.grid(art.HEX, 24)
    br = bronze("grille")
    red = pal("grille_red", 0x76, metallic=0.1, roughness=0.3, glow=0.9)
    red_hot = pal("grille_red_hot", 0x79, metallic=0.05, roughness=0.25, glow=1.3)
    floor = pal("grille_floor", 0x72, metallic=0.2, roughness=0.5)

    def slot_depth(x, y):
        d = 0.0
        for a, b, hw in GRILLE_SLOTS:
            dist = segment_distance(x, y, a, b)
            d = max(d, q.smoothstep(hw + 0.55, hw - 0.1, dist))
        return d

    def z_of(x, y, e):
        r = math.hypot(x / 9.0, y / 11.0)
        z = 1.0 + (GRILLE_H - 1.0) * e + 0.7 * max(0.0, 1.0 - r * r)
        return z - 1.9 * slot_depth(x, y)

    polys = q.pixel_polys(g, lambda v, c, r: True, ORIGIN, smooth=2, epsilon=0.35)
    plate = q.heightfield("plate", polys, z_of, br[9], spacing=0.3, edge=1.6)
    q.w.simplify_bottom(plate)
    shade = q.shades(g, ORIGIN, keep=lambda v: v >> 4 == 1, blur=1)

    def pick(c, n):
        if slot_depth(c.x, c.y) > 0.6:
            return floor
        s = 9.0 + (shade(c.x, c.y) - 8.0) * 0.6
        if n.z < 0.45:
            s -= 3.0
        return br[int(min(14, max(3, round(s))))]
    q.paint_faces(plate, pick)
    q.decimate(plate, 3600)
    parts = [plate]
    for i, (a, b, hw) in enumerate(GRILLE_SLOTS):
        a, b = Vector((a[0], a[1], 0.0)), Vector((b[0], b[1], 0.0))
        d = (a - b).normalized()
        length = (a - b).length
        mid = (a + b) / 2
        z = z_of(mid.x, mid.y, 1.0) + 0.55
        prof = [(0.0, 0.01), (0.25, 0.55 * hw), (0.8, 0.85 * hw), (length * 0.5, hw * 0.92),
                (length - 0.8, 0.85 * hw), (length - 0.25, 0.55 * hw), (length, 0.01)]
        prof = sorted(prof)
        parts.append(q.lathe_axis(f"bar{i}", prof, red, (b.x, b.y, z), tuple(d), 20, squash=0.55))
        core = [(0.6, 0.01), (1.2, 0.35 * hw), (length * 0.5, 0.45 * hw), (length - 1.2, 0.35 * hw), (length - 0.6, 0.01)]
        parts.append(q.lathe_axis(f"bar_core{i}", core, red_hot, (b.x, b.y, z + 0.35), tuple(d), 14, squash=0.6))
    return parts


if __name__ == "__main__":
    q.run()
