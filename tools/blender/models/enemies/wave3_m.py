"""Enemies of wave 3, batch M (sheet J: TORM, BOTANY A, BONUS), the green machines; modelled as their
sprites look (models.cfg: yaw=0). The big green shell of ?TUNNEL? is in wave3_m_shell.py (the grey
machines on the foliage: polish_window_block.py, polish_field_gun.py, polish_lens_pad.py, polish_eye_orb.py).
(The small green machine of TORM and BONUS, green_scarab (J 131), is built by polish_green_scarab.py, the green
tower, J 13 15 / 51 53, by polish_green_tower.py, the green skiff, J 169 207 / 245 283, by polish_green_skiff.py.)

- green_pod_ship (J 117): the green ship of TORM with bulging red pods at its sides, two lights glowing
  in each, a red crest with two lights at its top and its green hull narrowing to a point down the
  screen.

The pale parts are the light end of the green ramp (0x2c-0x2f), the claws the red ramp (0x70s).

usage: Blender -b --factory-startup -P wave3_m.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] 
"""
import math
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_m_kit as w  # noqa: E402
from wave3_m_kit import art, k, sh, pal, model, J  # noqa: E402


def greens(prefix):
    """The green machines' materials, by shade."""
    return {
        "dark": pal(f"{prefix}_green_dark", 0x23, metallic=0.35, roughness=0.45),
        "deep": pal(f"{prefix}_green_deep", 0x25, metallic=0.4, roughness=0.4),
        "green": pal(f"{prefix}_green", 0x28, metallic=0.45, roughness=0.35),
        "mid": pal(f"{prefix}_green_mid", 0x29, metallic=0.45, roughness=0.32),
        "light": pal(f"{prefix}_green_light", 0x2a, metallic=0.45, roughness=0.3),
        "pale": pal(f"{prefix}_pale", 0x2c, metallic=0.2, roughness=0.25),
        "cream": pal(f"{prefix}_cream", 0x2d, metallic=0.15, roughness=0.18),
        "glass": pal(f"{prefix}_canopy", 0x2e, metallic=0.1, roughness=0.08),
        "red": pal(f"{prefix}_red", 0x74, metallic=0.4, roughness=0.35),
        "red_dark": pal(f"{prefix}_red_dark", 0x71, metallic=0.35, roughness=0.45),
        "red_light": pal(f"{prefix}_red_light", 0x76, metallic=0.4, roughness=0.3),
        "core": pal(f"{prefix}_core", 0x7c, metallic=0.0, roughness=0.3, glow=1.6),
        "lamp": pal(f"{prefix}_lamp", 0x77, metallic=0.0, roughness=0.25, glow=1.1),
        "orange": pal(f"{prefix}_orange", 0x7a, metallic=0.0, roughness=0.3, glow=1.4),
        "slot": pal(f"{prefix}_slot", 0x21, metallic=0.3, roughness=0.6),
    }


# --- J 131: the green scarab -----------------------------------------------------------------------

# --- J 117: the green pod ship -----------------------------------------------------------------------

@model("green_pod_ship", [(J, 117, True)])
def green_pod_ship():
    """A wide green collar with a red crest along its top edge (two lights glowing in it), a green
    hull below it narrowing to a point down the screen with a ridge along its middle, and a red pod
    at each side of the hull, bulging lower down, with two lights glowing in it."""
    g = w.grid(art.J117, 24)
    m = greens("podship")
    rows = w.regions(g, lambda v, c, r: "h" if v >> 4 == 2 and r >= 2 else ".")

    def ridge(x, y, z):
        return z + 0.5 * math.exp(-((x - 0.5) / 0.9) ** 2) * min(1.0, max(0.0, z - 1.0) / 2.0)
    hull = w.part("hull", rows, "h", m["green"], sh.round_profile(0.75, max_height=5.4), bottom=0.3, z_fn=ridge,
                  spacing=0.5, epsilon=0.35, sigma=1.4)
    w.decimate(hull, 1800)
    k.smooth(hull, 50)
    w.paint_faces(hull, lambda c, n: m["deep"] if n.z < 0.25 else m["light"] if n.z > 0.85 and c.y > 7.0 else
                  m["mid"] if n.z > 0.9 else None)
    # The collar's rim along the top of the hull, the ridge down its middle.
    w.tube("collar_rim", [(-9.0, 8.4, 3.0), (-4.0, 7.2, 4.6), (0.5, 7.0, 5.0), (5.0, 7.2, 4.6), (10.0, 8.4, 3.0)], 0.7,
           m["mid"], 8)
    w.tube("ridge", [(0.5, 6.5, 5.6), (0.5, 0.0, 5.3), (0.5, -6.0, 4.2), (0.5, -10.5, 2.2)], 0.5, m["light"], 8)
    # The red crest along the top edge and its two lights.
    crest = w.sphere("crest", (0.5, 12.4, 2.6), (6.6, 2.0, 2.0), m["red_light"], 24, 10)
    w.paint_faces(crest, lambda c, n: m["red_dark"] if n.z < 0.1 else None)
    for x in (-2.0, 3.2):
        w.sphere(f"crest_light{x}", (x, 12.7, 4.1), (1.3, 0.8, 0.6), m["orange"], 12, 6)
    # The pods at the hull's sides, bulging lower down, two lights glowing in each.
    pod_profile = k.profile([(0.0, 0.01), (0.5, 1.3), (2.0, 1.85), (7.0, 2.2), (11.0, 2.35), (13.2, 1.9), (14.4, 0.01)],
                            0.6)
    for x in (-6.0, 7.0):
        w.lathe_axis(f"pod{x}", pod_profile, m["red_light"], (x, 6.8, 2.7), (0, -1, 0), 18)
        for y, size in ((3.4, 0.8), (-3.8, 1.15)):
            w.sphere(f"pod_light{x}{y}", (x + (0.4 if x < 0 else -0.4), y, 4.5), (size, size * 1.5, 0.55), m["orange"], 12, 6)


w.run()
