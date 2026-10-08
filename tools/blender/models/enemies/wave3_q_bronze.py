"""Batch Q of wave 3 (sheet A: SOH JIN), the bronze pieces on the ground; modelled as their sprites look
(models.cfg: yaw=0).

- bronze_grille (A 89): a bronze plate, an elongated hexagon lying on the ground, with three slanting slots
  side by side (the middle one longest) in which red bars glow.
- bronze_whorl (A 91; its frames A 129 only light its slot): a thick bronze ring with a dished middle, a
  lug at its upper right and a drip running down from its bottom, a red light glowing in its opening at
  the lower left. The sprite stands on a square of the ground's brown earth: that is the map's ground, which
  the game draws under it, so the model has none of it (batch AV) and stands on the 3D ground.

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


# --- A 91: the bronze whorl --------------------------------------------------------------------------

WHORL = Vector((-2.3, 1.4, 2.6))   # the ring's centre
WHORL_R, WHORL_TUBE = 5.3, 2.3
WHORL_GAP = 222.0                  # the opening, at the lower left (degrees)


@q.model("bronze_whorl", [(91, True)])
def bronze_whorl():
    br = bronze("whorl")
    red = pal("whorl_red", 0x75, metallic=0.1, roughness=0.3, glow=1.0)
    red_hot = pal("whorl_red_hot", 0x79, metallic=0.05, roughness=0.25, glow=1.4)
    dish = pal("whorl_dish", 0x15, metallic=0.55, roughness=0.4)
    parts = []

    # No mound of earth under it: the sprite's earth is the map's ground (batch AV).

    # The ring: a thick C, heavier at the upper left (the sprite's bright crescent), open at the lower left.
    gap = math.radians(WHORL_GAP)
    path, radii = [], []
    for i in range(53):
        a = gap + math.radians(30) + math.radians(300) * i / 52
        path.append((WHORL.x + WHORL_R * math.cos(a), WHORL.y + WHORL_R * math.sin(a), WHORL.z))
        radii.append(WHORL_TUBE + 0.35 * math.cos(a - math.radians(135)))
    ring = q.tube("ring", path, radii, br[11], 18, squash=0.95)
    q.paint_faces(ring, lambda c, n: br[6] if n.z < 0.1 else None)
    parts.append(ring)
    # The red light in the opening, glowing.
    lc = Vector((WHORL.x + WHORL_R * math.cos(gap), WHORL.y + WHORL_R * math.sin(gap), WHORL.z))
    tangent = (-math.sin(gap), math.cos(gap), 0.0)
    prof = [(-3.2, 0.01), (-2.6, 1.15), (0.0, 1.7), (2.6, 1.15), (3.2, 0.01)]
    parts.append(q.lathe_axis("light", prof, red, tuple(lc), tangent, 20, squash=0.95))
    core = [(-2.2, 0.01), (-1.6, 0.6), (0.0, 0.85), (1.6, 0.6), (2.2, 0.01)]
    parts.append(q.lathe_axis("light_core", core, red_hot, tuple(lc + Vector((0.2, 0.2, 1.05))), tangent, 16,
                              squash=0.7))
    # The dish in its middle.
    parts.append(q.lathe_axis("dish", [(-0.6, 0.01), (-0.5, 3.4), (0.3, 3.9), (0.6, 3.2), (0.65, 0.01)], dish,
                              (WHORL.x, WHORL.y, WHORL.z - 0.4), (0, 0, 1), 28, up=(0, 1, 0)))
    parts.append(q.sphere("boss", (WHORL.x + 0.3, WHORL.y - 0.2, WHORL.z + 0.2), (1.6, 1.6, 0.9), br[9], 16, 8))
    # The lug at the upper right.
    lug_at = Vector((4.6, 8.9, 3.0))
    parts.append(q.tube("lug_arm", [tuple(WHORL + Vector((3.9, 4.3, 0.2))), tuple(lug_at - Vector((0.6, 0.7, 0.3)))], 1.3,
                        br[10], 12))
    parts.append(q.sphere("lug", tuple(lug_at), (1.7, 1.6, 1.5), br[12], 16, 8))
    # The drip down from its bottom.
    drip = q.catmull([(-1.7, -2.6, 2.4), (-1.6, -5.0, 2.0), (-2.2, -7.4, 1.5), (-2.7, -9.2, 1.2)], 0.4)
    radii = [1.6 - 0.8 * (i / (len(drip) - 1)) ** 0.7 for i in range(len(drip))]
    parts.append(q.tube("drip", [tuple(p) for p in drip], radii, br[10], 12))
    parts.append(q.sphere("drop", (-2.75, -9.5, 1.2), (1.05, 1.15, 0.9), br[10], 14, 8))
    return parts


if __name__ == "__main__":
    q.run()
