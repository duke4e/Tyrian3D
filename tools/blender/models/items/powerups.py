"""Power-ups: the weapon and sidekick pick-ups of the power-ups sheet ("twoplayer" in the catalogue)
that enemies leave, mostly in arcade and two-player games. Each is an orb in the colour of its kind
with the weapon's symbol in front (powerups_parts.py has the shared parts):

- rear weapons (31009-31022), red orbs: powerups_rear.py
- sidekicks (32001-32015) and the dragonwing (30000), green orbs: powerups_sidekicks.py
- (the front weapons, 30001-30031, ice-blue orbs: polish_powerups_front.py; the special weapons, 32101-32106,
  and the dual MegaLaser's brown orb, 32115: polish_powerups_specials.py)

Every model is coloured as its sprite (palette materials), so they are not recoloured
(color=sprite); models.cfg turns them slowly (spin).

usage: Blender -b --factory-startup -P powerups.py -- [--only <name>,...] [--preview <directory>]
           [--check <powerups sheet.png>] [--out <directory>]
--preview renders <directory>/<name>_top.png and _3q.png; --check prints each model's silhouette
overlap with its sprite.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402
import bpy  # noqa: E402
import powerups_parts  # noqa: E402
import powerups_rear  # noqa: E402
import powerups_sidekicks  # noqa: E402

MODELS = {}
for module in (powerups_rear, powerups_sidekicks):
    MODELS.update(module.MODELS)


def main():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    out = options.get("out", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "items"))
    for name, (sprite, build) in MODELS.items():
        if only and name not in only:
            continue
        k.reset()
        build()
        powerups_parts.merge_by_material()
        if "check" in options:
            print(f"{name} (powerups {sprite}):")
            k.check_silhouette(options["check"], [sprite])
        k.export(os.path.join(out, name + ".glb"))
        if "preview" in options:
            os.makedirs(options["preview"], exist_ok=True)
            # The game clamps colours rather than tone-mapping them (glowing parts stay saturated).
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(os.path.join(options["preview"], name))


main()
