"""Batch AR of wave 3, sheet # (written x23 in models.cfg): the spinning claw and the dark sawblade of IXMUCANE,
SAWBLADES and ?TUNNEL?, each four 2x2 sprites meeting at their shared corner (the levels place them as a square:
top left, top right, and the two below), built whole, cut into the four pieces and drawn at their own origins
(origin) so they meet; authored as the sprites look (yaw=0). Kit: wave3_ar_kit.py.

The pieces never animate by themselves: level events start their animations (event 24 on their link), which run
through frames of the enemy data beyond its first:

- The claw (enemies 426-429, 153 155 above 191 193): it unfolds out of a small dark knot (153), growing and
  lighting up through 89, 85 and 81 to the full claw (77), then spins for ever: 13, 9, 5, 1, 13... (the claw turning
  counter-clockwise about 22.5 degrees a frame: 13 is it turned 25 degrees clockwise, 9 the full claw as 77 draws
  it, 5 and 1 it turned 25 and 45 degrees counter-clockwise). What it is: a bronze hub with a glowing yellow lamp,
  four steel arms out of it, each ending in a pincer (a long hooked blade and a short prong).
  Models spin_claw_<sprite> for every frame's four pieces: the first frame's (153 155 191 193) for the sprite lines,
  the others for frame lines. The unfolding is the claw scaled about its hub (as the frames draw it), its steel
  darker the smaller it is; the spin frames are the full claw turned about its hub.
- The dark sawblade (enemies 430-433, 233 235 above 271 273): the claw's hub and arms with a blue gem for a hub and
  two more blades in each quarter (a strut out of the hub carrying a long blade and a short one, all pointing round
  the wheel). Dark at first (233), it lights up (229, 165) and then spins (161, 157, 161...: 161 is 157 turned 22.5
  degrees clockwise). Models dark_saw_<sprite>: the first frame's (233 235 271 273) and the frames' (229 231 267
  269, 165 167 203 205, 161 163 199 201, 157 159 195 197). Same shape in 233, 229, 165 and 157 (only the steel's
  shade changes).

The frames' sprites 13, 9, 5, 1 (and the other pieces') are in the sawblade's enemy data too, but its events never
show them.

usage: Blender -b --factory-startup -P wave3_ar_saw.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole <prefix>]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ar_kit as kit  # noqa: E402
from wave3_ar_kit import k, w, pal  # noqa: E402

HUB = (0.5, 0.5)    # the hub's centre: pixel (24, 27) of the four sprites (their shared corner at (24, 28))
STEM = "enemy_x23"


def steel(level, prefix="claw"):
    """The steel's materials for a frame whose arms are drawn up to grey shade `level` (higher is lighter)."""
    def g(i):
        return max(2, min(13, i))
    return {
        "top": pal(f"{prefix}_steel_top", g(level - 1), metallic=0.5, roughness=0.32),
        "upper": pal(f"{prefix}_steel_upper", g(level - 3), metallic=0.5, roughness=0.36),
        "side": pal(f"{prefix}_steel_side", g(level - 5), metallic=0.45, roughness=0.42),
        "under": pal(f"{prefix}_steel_under", 0x02, metallic=0.4, roughness=0.5),
        "edge": pal(f"{prefix}_steel_edge", g(level + 1), metallic=0.7, roughness=0.25),
    }


def paint_steel(obj, m):
    return kit.banded(obj, [(0.8, m["top"]), (0.35, m["upper"]), (-0.25, m["side"]), (-2.0, m["under"])])


def rel(points):
    """Points given relative to the hub (x, y, z, half width) moved to the whole's coordinates."""
    return [(HUB[0] + x, HUB[1] + y, z, r) for x, y, z, r in points]


# --- One arm (pointing up the screen; the others are it turned) ----------------------------------------------------

ROD = [(0.0, 3.0, 4.0, 1.9), (0.2, 6.5, 4.2, 2.0), (0.5, 10.3, 4.4, 2.2)]
PALM = [(-5.0, 11.6, 4.6, 1.35), (-1.0, 11.6, 4.6, 1.6), (2.5, 11.7, 4.6, 1.6), (4.6, 12.0, 4.6, 1.35)]
SICKLE = [(-2.6, 12.0, 4.6, 2.3), (-2.6, 14.0, 4.9, 2.4), (-2.0, 16.0, 5.3, 2.4), (-0.9, 17.2, 5.6, 2.35),
          (1.0, 19.0, 6.0, 2.3), (3.0, 21.0, 6.5, 2.2), (4.8, 22.6, 7.0, 1.9), (5.6, 23.0, 7.2, 1.3)]
PRONG = [(3.4, 12.4, 4.6, 1.7), (4.5, 13.3, 4.8, 1.7), (6.2, 15.1, 5.2, 1.7), (7.9, 16.8, 5.6, 1.55),
         (8.6, 17.5, 5.8, 1.1)]


def arm(name, m, dark):
    """A steel arm out of the hub: a rod, a collar where it leaves the hub, the pincer's palm, its long hooked
    blade (curving out, then round towards the right) and its short prong."""
    parts = [kit.blade(f"{name}_rod", rel(ROD), m["top"], squash=0.95, segments=12),
             kit.blade(f"{name}_palm", rel(PALM), m["top"], squash=0.85, segments=12),
             kit.blade(f"{name}_sickle", rel(SICKLE), m["top"], squash=0.42, segments=8, smooth_angle=35),
             kit.blade(f"{name}_prong", rel(PRONG), m["top"], squash=0.45, segments=8, smooth_angle=35)]
    for obj in parts:
        paint_steel(obj, m)
    collar = w.lathe_axis(f"{name}_collar", [(0.0, 2.15), (0.3, 2.3), (1.1, 2.3), (1.4, 2.05)], dark,
                          (HUB[0] + 0.05, HUB[1] + 4.6, 4.0), (0.05, 1.0, 0.04), segments=14, smooth_angle=40)
    parts.append(collar)
    return parts


# --- The sawblade's extra blades (the quarter up and right of the hub; the others are it turned) -------------------

STRUT = [(5.4, 3.6, 3.6, 2.0), (7.0, 7.3, 3.8, 2.2), (8.4, 10.4, 4.0, 2.0)]
BLADE_A = [(5.4, 13.0, 4.8, 2.0), (9.0, 13.3, 4.9, 2.25), (14.0, 13.2, 5.0, 2.15), (18.3, 12.6, 5.2, 1.8),
           (21.0, 11.7, 5.4, 0.9)]
BLADE_B = [(8.0, 6.7, 4.3, 1.65), (12.0, 6.8, 4.4, 1.65), (16.3, 6.5, 4.5, 1.4), (19.4, 5.8, 4.7, 0.7)]


def saw_blades(name, m):
    parts = [kit.blade(f"{name}_strut", rel(STRUT), m["top"], squash=0.6, segments=10),
             kit.blade(f"{name}_a", rel(BLADE_A), m["top"], squash=0.4, segments=8, smooth_angle=35),
             kit.blade(f"{name}_b", rel(BLADE_B), m["top"], squash=0.42, segments=8, smooth_angle=35)]
    for obj in parts:
        paint_steel(obj, m)
    return parts


# --- Hubs ------------------------------------------------------------------------------------------------------------

def bronze_hub():
    """The claw's hub: a bronze dome on a dark band, a yellow lamp glowing on its crown (up and left, where the
    sprites draw it)."""
    light = pal("claw_hub_light", 0x1a, metallic=0.75, roughness=0.28)
    mid = pal("claw_hub_mid", 0x17, metallic=0.75, roughness=0.32)
    dark = pal("claw_hub_dark", 0x14, metallic=0.7, roughness=0.38)
    band = pal("claw_hub_band", 0xa3, metallic=0.55, roughness=0.45)
    lamp_m = pal("claw_lamp", 0x7c, metallic=0.0, roughness=0.2, glow=1.6)
    lamp_rim = pal("claw_lamp_rim", 0x7a, metallic=0.0, roughness=0.25, glow=0.8)
    dome = w.column("hub", [(0.0, 4.4), (1.5, 5.3), (4.0, 5.6), (6.2, 5.0), (7.8, 3.7), (8.8, 2.0), (9.2, 0.0)], mid,
                    HUB[0], HUB[1], segments=20, smooth_angle=50)
    kit.banded(dome, [(0.75, light), (0.3, mid), (-0.2, dark), (-2.0, band)])
    ring = w.hoop("hub_band", (HUB[0], HUB[1], 3.6), [(5.5, -0.7), (5.95, -0.45), (6.0, 0.45), (5.5, 0.7)], band,
                  segments=24)
    lamp = w.sphere("hub_lamp", (HUB[0] - 1.4, HUB[1] + 1.7, 8.0), (1.55, 1.4, 0.75), lamp_m, segments=16, rings=8)
    kit.banded(lamp, [(0.5, lamp_m), (-2.0, lamp_rim)])
    return [dome, ring, lamp]


def gem_hub():
    """The sawblade's hub: a faceted blue gem in a dark steel bezel."""
    bezel = pal("saw_bezel", 0x05, metallic=0.6, roughness=0.4)
    facets = [pal("saw_gem_98", 0x98, metallic=0.1, roughness=0.15, glow=0.25),
              pal("saw_gem_9a", 0x9a, metallic=0.1, roughness=0.12, glow=0.35),
              pal("saw_gem_9c", 0x9c, metallic=0.1, roughness=0.1, glow=0.45),
              pal("saw_gem_8f", 0x8f, metallic=0.1, roughness=0.08, glow=0.6)]
    base = w.column("gem_bezel", [(0.0, 5.4), (1.2, 5.9), (3.6, 6.0), (4.3, 5.6), (4.4, 0.0)], bezel, HUB[0], HUB[1],
                    segments=8, smooth_angle=30)
    gem = w.column("gem", [(3.6, 5.3), (4.8, 5.2), (6.8, 3.8), (8.2, 2.0), (8.6, 0.0)], facets[1], HUB[0], HUB[1],
                   segments=8, smooth_angle=10)
    kit.turn_z([base, gem], 22.5, HUB)

    def pick(c, nrm):
        if nrm.z > 0.9:
            return facets[3] if c.x < HUB[0] and c.y > HUB[1] else facets[2]
        lit = -nrm.x * 0.6 + nrm.y * 0.5
        return facets[2] if lit > 0.3 else facets[1] if lit > -0.2 else facets[0]
    w.paint_faces(gem, pick)
    return [base, gem]


# --- The whole objects -----------------------------------------------------------------------------------------------

def claw(scale=1.0, level=9, turn=0.0):
    """The claw: scale its size about the hub (the unfolding frames), level the steel's shade, turn the degrees it
    is turned counter-clockwise (the spin frames)."""
    m = steel(level)
    dark = pal("claw_collar", 0x03, metallic=0.5, roughness=0.45)
    objs = bronze_hub()
    for i in range(4):
        parts = arm(f"arm{i}", m, dark)
        kit.turn_z(parts, -90.0 * i, HUB)
        objs += parts
    if turn:
        kit.turn_z(objs, turn, HUB)
    if scale != 1.0:
        kit.scale_about(objs, scale, HUB)


def saw(level=11, turn=0.0):
    """The sawblade: the claw's four arms round a blue gem, a strut with two blades in each quarter."""
    m = steel(level, "saw")
    dark = pal("saw_collar", 0x03, metallic=0.5, roughness=0.45)
    objs = gem_hub()
    for i in range(4):
        parts = arm(f"arm{i}", m, dark) + saw_blades(f"quarter{i}", m)
        kit.turn_z(parts, -90.0 * i, HUB)
        objs += parts
    if turn:
        kit.turn_z(objs, turn, HUB)


# The claw's frames: top left sprite -> (scale, steel shade, turn). 153 is the first frame (the sprite lines).
CLAW = {153: (0.5, 5, 0.0), 89: (0.85, 7, 0.0), 85: (0.93, 8, 0.0), 81: (1.0, 8, 0.0), 77: (1.0, 9, 0.0),
        13: (1.0, 10, -25.0), 9: (1.0, 10, 0.0), 5: (1.0, 10, 25.0), 1: (1.0, 11, 45.0)}
# The sawblade's: 233 is the first frame.
SAW = {233: (5, 0.0), 229: (7, 0.0), 165: (9, 0.0), 161: (10, -22.5), 157: (11, 0.0)}

for s, (scale, level, turn) in CLAW.items():
    kit.pieced(f"spin_claw_{s}", lambda scale=scale, level=level, turn=turn: claw(scale, level, turn), (48, 56),
               kit.quad_pieces("spin_claw_", STEM, s))
for s, (level, turn) in SAW.items():
    kit.pieced(f"dark_saw_{s}", lambda level=level, turn=turn: saw(level, turn), (48, 56),
               kit.quad_pieces("dark_saw_", STEM, s))


if __name__ == "__main__":
    kit.run()
