"""The blue canister of the shots sheet (sprite 90), as its sprite is drawn: the last shot sprite without a model, found by
the sweep of every level (2026-10-30: fired in ASTCITY by weapon 535, which no port, sidekick or special list names).

- shot_canister_blue (90): a steel-blue canister, two rounded caps of polished ramp 3 steel either side of a narrower
  window of blue glass glowing in its own colour (ramp 9) round a brighter core, a dark lip at its base (the sprite's
  feet)

The sprite: columns 3-8 (x = 0), rows 0-13: the top cap (rows 0-4, its tip the outline 0x52), the window (rows 5-8,
columns 4-7: 0x94 at its edges to 0x9e in its middle, an outline either side), the bottom cap (rows 9-12), the feet
(row 13, outline only); the caps' middle columns bright (0x3c-0x3f), their edges darker (0x35-0x37). Built with
Batch AS's kit (shot_kit.py) as the Atomic RailGun's canister is (shots_objects.py rail_canister).

Run: Blender -b --factory-startup -P polish_shot_canister.py -- [--only ...] [--sheets <dir>] [--preview <dir>]
     [--cfg <dir>]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shot_kit as sk  # noqa: E402
from shot_kit import k, model, s  # noqa: E402


@model("shot_canister_blue", ("shots", 90), [("shots", 90, 0, "", "weapon 535 (ASTCITY)")],
       note="steel-blue canister, a window of blue glass glowing between two polished caps")
def canister_blue():
    steel = sk.pal("cb_steel", 0x3b, metallic=0.55, roughness=0.2)
    pale = sk.pal("cb_pale", 0x3e, metallic=0.55, roughness=0.15)
    dark = sk.pal("cb_dark", 0x52, metallic=0.4, roughness=0.4)
    glass = sk.pal("cb_glass", 0x96, metallic=0.1, roughness=0.08, glow=k.level_palette()[0x97], strength=0.25)
    core = sk.pal("cb_core", 0x9d, metallic=0.1, roughness=0.05, glow=k.level_palette()[0x9e], strength=0.5)
    # The caps take in half the sprite's outline (columns 2 and 9), the window the outline beside it (columns 3, 8).
    profile = [(-6.9, 2.0), (-6.6, 2.8), (-6.0, 3.25), (-5.6, 3.4), (-2.4, 3.4), (-2.1, 3.0), (-1.9, 2.55),
               (1.9, 2.55), (2.1, 3.0), (2.4, 3.4), (5.4, 3.4), (6.0, 3.1), (6.5, 2.5), (6.85, 1.6), (7.0, 0.0)]
    sk.body("cb_body", profile, [(-6.9, -6.0, dark), (-6.0, -2.15, steel), (-2.15, -0.75, glass), (-0.75, 0.95, core),
                                 (0.95, 2.15, glass), (2.15, 5.2, steel), (5.2, 6.4, pale), (6.4, 7.0, dark)],
            step=0.45, segments=14)


if __name__ == "__main__":
    sk.run()
