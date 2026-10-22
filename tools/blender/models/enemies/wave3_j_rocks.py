"""Enemies of wave 3, batch J (sheet D, the asteroid levels), the rocks; modelled as
their sprites look (models.cfg: yaw=0). The machines are in wave3_j.py; the two big asteroids (D 1 3 / 39 41 and
D 7 9 / 45 47) in polish_asteroids.py; the small rocks (D 95, 114, 133, 152) in polish_pebbles.py; the sky rocks D 43, 85 and 123 in
polish_sky_rocks.py; the huge asteroid (D 13 ... 91) in polish_crag.py.

- rock_beacon (D 93): a faceted asteroid with a red beacon on its side (its frames 55 and 18 light
  the beacon: it glows).
- rock_blue_eye (D 229): a faceted asteroid with a blue light set in its middle (its frames 231-235
  light it up: it glows).

usage: Blender -b --factory-startup -P wave3_j_rocks.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_j_kit as w  # noqa: E402
from wave3_j_kit import art, sh, pal, model  # noqa: E402

D = "enemy_D"


# --- Asteroids in the sky (D 93, 229) ------------------------------------------------

def sky_rock(g, prefix, seed, height=6.6, depth=None):
    """A faceted grey asteroid over the sprite's outline (as asteroid_lumpy)."""
    shades = [pal(f"{prefix}_{i:x}", i, metallic=0.1, roughness=0.75) for i in range(0x04, 0x0d)]
    rows = w.regions(g, lambda v, c, r: "#")
    poly = max(sh.outlines(rows, "#", (12, 14), smooth=2, epsilon=0.3), key=len)
    shade = w.sampler(g, (12, 14), value=lambda v: v & 15 if v >> 4 == 0 else 8, blur=1,
                      keep=lambda v: v is not None and v != 0x20)

    def shade_of(c, n):
        # The sprite's shade where the facet lies, a little lighter facing the sun.
        s = shade(c.x, c.y) - 4.0 + 1.5 * (-0.45 * n.x + 0.35 * n.y + 0.8 * n.z)
        return s if n.z > -0.2 else 0.5
    return w.faceted_rock("rock", poly, height, shades, seed=seed, depth=depth, shade_of=shade_of)


@model("rock_beacon", [(D, 93, True)])
def rock_beacon():
    """A faceted asteroid with a red beacon on its right side: a steel housing round a glowing lamp
    (frames 55 and 18 light it)."""
    rock = sky_rock(w.grid(art.D93, 24), "rock_beacon", 17, height=6.6)
    steel = pal("beacon_steel", 0x66, metallic=0.7, roughness=0.3)
    lamp = pal("beacon_lamp", 0x77, metallic=0.0, roughness=0.3, glow=1.4)
    x, y = w.px(19.0), w.py(12.0)
    z = sh.surface_z(rock, x, y, 4.0)
    w.rounded_box("beacon_housing", (x, y, z - 0.2), (3.8, 5.6, 2.6), steel, bevel=0.6)
    w.sphere("beacon_lamp", (x, y, z + 0.9), (1.5, 2.3, 1.2), lamp, 16, 8)


@model("rock_blue_eye", [(D, 229, True)])
def rock_blue_eye():
    """A faceted asteroid with a blue light set in its middle (frames 231-235 light it)."""
    rock = sky_rock(w.grid(art.D229, 24), "rock_blue_eye", 29, height=6.6)
    blue = pal("blue_eye", 0x9c, metallic=0.1, roughness=0.15, glow=1.2)
    rim = pal("blue_eye_rim", 0x99, metallic=0.4, roughness=0.3)
    x, y = w.px(12.0), w.py(14.0)
    z = sh.surface_z(rock, x, y, 5.0)
    w.lathe_axis("eye_rim", [(-1.0, 2.4), (0.2, 2.4), (0.5, 1.9), (0.55, 1.4)], rim, (x, y, z - 0.3), (0, 0, 1), 16,
                 up=(0, 1, 0))
    w.sphere("eye", (x, y, z + 0.1), (1.6, 1.6, 1.0), blue, 16, 8)
    # Four short rays (the sprite's cross of light).
    for a in range(4):
        d = Vector((math.cos(a * math.pi / 2), math.sin(a * math.pi / 2), 0))
        w.sphere(f"ray{a}", (x + d.x * 2.0, y + d.y * 2.0, z + 0.05), (0.7 + 0.5 * abs(d.x), 0.7 + 0.5 * abs(d.y), 0.5),
                 blue, 10, 5)


w.run()
