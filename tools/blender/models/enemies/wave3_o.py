"""Batch O of wave 3 (sheet K, CAMANIS), the sparks; modelled as their sprites look (models.cfg: yaw=0). (The
WARNING sign: polish_warning.py; the wall of fire: polish_fire_wall.py.) The grey machines of sheet K are in
wave3_o_machines.py.

- spark_dot (K 124), spark_glint (K 125): CAMANIS' two tiny white sparks (1x1): a glowing bead and a
  four-pointed glint.

usage: Blender -b --factory-startup -P wave3_o.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_o_kit as o  # noqa: E402
from wave3_o_kit import pal  # noqa: E402


# --- K 124, 125: CAMANIS' sparks (1x1) -------------------------------------------------------------

@o.model("spark_dot", [(124, False)], size=(12, 14))
def spark_dot():
    """A white bead, glowing, with a brighter core showing through its top."""
    shell = pal("spark_shell", 0x0b, metallic=0.2, roughness=0.25, glow=0.6)
    core = pal("spark_core", 0x0f, metallic=0.0, roughness=0.2, glow=1.2)
    o.sphere("bead", (0.0, 0.0, 0.0), (2.1, 2.1, 1.9), shell, 20, 10)
    o.sphere("core", (-0.2, 0.2, 0.75), (1.35, 1.35, 1.3), core, 16, 8)


@o.model("spark_glint", [(125, False)], size=(12, 14))
def spark_glint():
    """A four-pointed glint: a glowing white bead with four tapering rays along the axes."""
    ray = pal("glint_ray", 0x0a, metallic=0.2, roughness=0.3, glow=0.6)
    core = pal("glint_core", 0x0f, metallic=0.0, roughness=0.2, glow=1.2)
    cx, cy = 0.5, 0.5
    o.sphere("bead", (cx, cy, 0.0), (1.7, 1.7, 1.5), core, 16, 8)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        o.lathe_axis(f"ray{dx}{dy}", [(0.0, 1.2), (1.2, 0.9), (2.2, 0.45), (2.7, 0.01)], ray, (cx, cy, 0.0),
                     (dx, dy, 0), 10, squash=0.8)


if __name__ == "__main__":
    o.run()
