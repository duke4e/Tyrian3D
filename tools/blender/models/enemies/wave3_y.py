"""Batch Y of wave 3 (sheet 8: IXMUCANE and SAWBLADES), the creatures and small ships, modelled as their
sprites look (models.cfg: yaw=0). The big spider (an object the game draws in pieces) is in wave3_y_boss.py; the
kit is wave3_y_kit.py, the pixels wave3_y_art.py. (The twin tube, 8 19: polish_twin_tube.py; the small crab, 8 267:
polish_tan_crab.py; the red ship with two prongs, 8 1: polish_prong_ship.py; the dome on two claws, 8 115:
polish_claw_dome.py; the rock wall: polish_ixm_wall_ends.py, polish_ixm_wall_slot.py, polish_ixm_wall_rock.py.)

- sawblades_carrot (8 129): SAWBLADES' carrot: an orange root with rings and a dark hollow at its middle, its green
  leaves on top.

usage: Blender -b --factory-startup -P wave3_y.py -- [--only name,name] [--preview <prefix>] [--check 1]
       [--stats 1]
"""
import math
import os
import sys

from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_y_kit as y  # noqa: E402
from wave3_y_kit import k, pal, tube, sphere, lathe_axis  # noqa: E402


# --- 8 129: the carrot -------------------------------------------------------------------------------

CARROT = y.frame("CARROT", 24, (12, 14))


def leaf(name, base, tip, width, mat, rib_mat, lift=2.0):
    """A leaf from base to tip (3D points): a thin blade, widest a third of the way, curving up by `lift`
    in its middle, a lighter rib along it."""
    b, t = Vector(base), Vector(tip)
    pts = []
    count = 12
    for i in range(count + 1):
        f = i / count
        p = b.lerp(t, f)
        p.z += lift * math.sin(math.pi * f) * 0.8
        pts.append(p)
    secs = [(max(0.12, width * math.sin(math.pi * min(1.0, (i / count) ** 0.8)) * (1.0 - 0.4 * i / count)), 0.22)
            for i in range(count + 1)]
    blade = y.loft_path(name, pts, secs, mat, segments=8, smooth_angle=70)
    tube(name + "_rib", [(p.x, p.y, p.z + 0.12) for p in pts[:-2]], 0.16, rib_mat, 6)
    return blade


@y.model("sawblades_carrot", lambda: y.frame_mask(CARROT))
def sawblades_carrot():
    """An orange root (a cone lying down the screen, rings round it) with a dark brown hollow in its middle
    round a lighter knob, and three green leaves fanning up the screen from its top."""
    ax, az = 0.5, 5.0
    orange = pal("carrot_orange", 0x7a, metallic=0.05, roughness=0.55)
    orange_light = pal("carrot_orange_light", 0x7c, metallic=0.05, roughness=0.5)
    orange_dark = pal("carrot_orange_dark", 0x77, metallic=0.05, roughness=0.6)
    ring_m = pal("carrot_ring", 0x79, metallic=0.05, roughness=0.6)
    hollow = pal("carrot_hollow", 0xb3, metallic=0.05, roughness=0.7)
    hollow_rim = pal("carrot_hollow_rim", 0xb6, metallic=0.05, roughness=0.6)
    knob = pal("carrot_knob", 0xb9, metallic=0.1, roughness=0.45)
    green = pal("carrot_green", 0xc4, metallic=0.05, roughness=0.55)
    green_light = pal("carrot_green_light", 0xc9, metallic=0.05, roughness=0.5)
    green_dark = pal("carrot_green_dark", 0xc1, metallic=0.05, roughness=0.6)

    # The root, along -y from its shoulder (y 5) to its tip (y -14); slight bulges between the rings.
    keys = [(0.0, 0.01), (0.4, 3.2), (1.0, 5.2), (2.0, 6.2), (3.5, 6.6), (5.5, 6.5), (7.5, 6.0), (9.5, 5.1),
            (11.5, 4.1), (13.5, 3.0), (15.5, 1.9), (17.4, 0.9), (18.6, 0.3), (19.0, 0.01)]
    prof = [(t, r) for t, r in k.profile(keys, 0.35)]
    rings_at = [4.0, 6.6, 9.2, 11.8, 14.3]
    prof = [(t, r * (1.0 - 0.07 * max(0.0, 1.0 - min(abs(t - ra) for ra in rings_at) / 0.45))) for t, r in prof]
    root = lathe_axis("root", prof, orange, (ax, 5.0, az), (0, -1, 0), segments=28, squash=0.78)
    y.paint_faces(root, lambda c, nrm: orange_dark if nrm.z < 0.25 else
                  ring_m if min(abs((5.0 - c.y) - ra) for ra in rings_at) < 0.22 else
                  orange_light if nrm.x < -0.3 and nrm.z > 0.5 else orange)
    # The hollow: a dark brown patch on its middle in a raised rim, a lighter knob in it.
    def root_z(x, yy):
        r = y.interp(prof, 5.0 - yy)
        return az + 0.78 * math.sqrt(max(0.0, r * r - (x - ax) ** 2))
    cx, cy = 0.0, -2.4
    y.heightfield("hollow", [y.ellipse(cx, cy, 2.3, 2.3, 28)], lambda x, yy: root_z(x, yy) + 0.12, hollow, spacing=0.4)
    y.ring_path("hollow_rim", [(cx + 2.35 * math.cos(a), cy + 2.35 * math.sin(a),
                                root_z(cx + 2.35 * math.cos(a), cy + 2.35 * math.sin(a)) + 0.1)
                               for a in [2 * math.pi * i / 32 for i in range(32)]], 0.5, hollow_rim, 8)
    sphere("knob", (cx - 0.3, cy + 0.3, root_z(cx, cy) + 0.1), (1.15, 1.15, 0.8), knob, 16, 8)
    # The leaves, from the top of the root.
    base_z = az + 2.6
    leaf("leaf_l", (ax - 0.6, 4.6, base_z), (ax - 5.8, 12.4, base_z + 1.0), 1.5, green, green_light, lift=2.2)
    leaf("leaf_m", (ax + 0.0, 4.8, base_z + 0.4), (ax - 0.2, 13.4, base_z + 2.0), 1.3, green, green_light, lift=2.6)
    leaf("leaf_r", (ax + 0.6, 4.6, base_z), (ax + 5.2, 10.2, base_z + 0.6), 1.4, green_dark, green, lift=1.8)
    lathe_axis("stalk", [(0.0, 1.5), (1.4, 1.1), (1.8, 0.01)], green_dark, (ax, 4.2, base_z - 0.6), (0, 1, 0.3),
               segments=12)


if __name__ == "__main__":
    y.run()
