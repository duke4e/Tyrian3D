"""Two special weapons' shots (shots sheet sprites 127, 128, 129 and 49, all 1x1: 12 x 14 cells), modelled (2026-10-30,
round 3 of the energy shots' models; until then each was drawn as its sprite with volume and the automatic glow).

Who fires them (specials are fired by pressing the fire button: each new press, while the special's wait is over):
  127 128 129  Protron Dispersal (special 12, weapon 670): for 14 + 4 x the front gun's power frames, a steel ball a
               frame from the ship, turning round its eight ways (6 pixels a frame); each ball shows the frames 126
               (the Wild Ball's steel ball, shot_steel_ball, shots_objects.py) 127 128 129 by turns: the steel
               brightening and dimming (127 two shades lighter than 126, 128 three to four, 129 = 127)
  49           Pulse Blast (special 17, weapon 753): two at a press, 22 apart, 10 behind the ship, flying up at 10
None picks its sprite by heading (yaw 0).

As the sprites draw them:
- 126-129 a steel ball 11 across (columns 0-10, rows 2-12; its middle x -0.5, y -0.5) inside a near-black outline
  (ramp 3, the steel blue-greys 0x30-0x3f): a highlight up and left (0x3f), a bright crescent down and right.
- 49 a teardrop of fire 9 wide (columns 1-9, rows 1-12; its middle column 5: x -0.5): a round head white in its upper
  middle (0x7f at rows 3-4), yellow and orange round it, a short tail tapering down to a pixel (orange, dark red).

The models:
- the steel ball's frames (shot_special_ball_127: 127 and 129; _128: 128): shot_steel_ball's ball (centre (-0.5, -0.5),
  radius 5.3) as the sprites paint it, lit from the upper left (polish_shot_protron.pearl: its bands in rings round the
  light's direction, each face in one): the highlight (0x3f), the steel darkening away from it a shade a band (to 0x3b;
  128 a shade lighter), a crescent a shade lighter again inside the rim at the lower right, each band glowing a little
  by its shade, so that the frames flash as the sprites do (shot_steel_ball, 126's model, a plain polished sphere: the
  dark frame between them). A plain sphere in a lighter steel read as a dull grey ball where the sprites flash white,
  and the sprites' own bands (a dark one between the highlight and the crescent) as a striped ball (Protron Dispersal in
  TYRIAN, 2026-10-30): the bands go a shade at a time.
- 49 (shot_special_blast): a teardrop of fire lofted along the screen's y (polish_shot_fireball.Loft, its bands of
  ramp 7 on the mesh's rings, both sides of its hot part), a white core standing out of its head
  (polish_shot_fireball.core).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
cell's centre (pixel 6, 7: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); built on z = 0 (the game centres shot
models in height on the player's layer: the balls' lines take height=, see the block's comment).

models.cfg: see the block's comment.

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_special.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] [--preview <prefix>]
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_fireball as kit  # noqa: E402
from polish_shot_fireball import k, mk, triangulate, view  # noqa: E402
from polish_shot_protron import Look, LIGHT, pearl  # noqa: E402
from polish_launched_flames import lit  # noqa: E402

OUTDIR = kit.OUTDIR

# === The steel ball's frames ==========================================================================================

# Bands by the angle from the light (degrees; the upper left, 37 degrees off straight up: from above, the top half of
# the ball reaches 127 degrees at the lower right rim): (to this angle, palette index, emission), as the sprites'
# pixels go.
BALLS = {  # name: (the look, the sprites)
    "shot_special_ball_127": (Look(axis=LIGHT, step=14.0, segments=20, height=0.94, roughness=0.18,
                                   bands=[(16.0, 0x3f, 0.5), (34.0, 0x3e, 0.44), (56.0, 0x3d, 0.38),
                                          (80.0, 0x3c, 0.32), (104.0, 0x3b, 0.26), (140.0, 0x3c, 0.32),
                                          (180.0, 0x3a, 0.22)]), (127, 129)),
    "shot_special_ball_128": (Look(axis=LIGHT, step=14.0, segments=20, height=0.94, roughness=0.18,
                                   bands=[(26.0, 0x3f, 0.56), (48.0, 0x3e, 0.48), (72.0, 0x3d, 0.42),
                                          (104.0, 0x3c, 0.34), (140.0, 0x3d, 0.4), (180.0, 0x3b, 0.28)]), (128,)),
}
BALL_CENTRE, BALL_RADIUS = (-0.5, -0.5), 5.3


def steel_ball(name, look):
    """The steel ball painted as the sprites paint it (polish_shot_protron.pearl): one material a palette index."""
    mats, seen = [], set()
    for _, index, glow in look.bands:
        if index not in seen:
            seen.add(index)
            mats.append(lit(f"special_steel_{index:02x}", index, glow, roughness=look.roughness))
    return [pearl(name + "_ball", look, BALL_CENTRE, BALL_RADIUS, mats)]


# === Pulse Blast's teardrop (49) ======================================================================================

BLAST = dict(
    x=-0.5, nose=6.0, tail=-6.0, depth=0.86,
    width=((0.0, 0.0), (0.02, 1.45), (0.06, 2.5), (0.12, 3.35), (0.2, 4.0), (0.3, 4.4), (0.42, 4.5), (0.52, 4.2),
           (0.6, 3.5), (0.7, 2.7), (0.8, 2.2), (0.88, 1.4), (0.95, 0.7), (1.0, 0.0)),
    along=((0.0, 6.5), (0.04, 8.0), (0.12, 12.5), (0.21, 15.2), (0.29, 15.2), (0.375, 14.2), (0.46, 13.2),
           (0.54, 12.2), (0.625, 11.2), (0.71, 10.2), (0.79, 9.2), (0.875, 7.4), (0.96, 4.6), (1.0, 3.5)),
    across=((0.0, 3.0), (0.15, 6.0), (0.3, 8.0), (0.5, 8.5), (0.75, 6.5), (1.0, 4.0)),
    core=(0.1, 0.36, 1.95, 0.42),
)
BLAST_BANDS = [(-99.0, 0x74, 0.26), (5.2, 0x76, 0.33), (7.0, 0x78, 0.4), (8.6, 0x79, 0.46), (9.8, 0x7a, 0.5),
               (11.0, 0x7b, 0.52), (12.2, 0x7c, 0.56), (13.2, 0x7d, 0.58)]
BLAST_CORE_BANDS = ((0.0, 0x7f, 0.62), (0.5, 0x7e, 0.6))


def blast(name):
    spec = BLAST
    length = spec["nose"] - spec["tail"]
    fire = kit.materials("blast_fire", BLAST_BANDS)
    body = kit.Loft(spec["x"], spec["nose"], spec["tail"], kit.curve(spec["width"]),
                    kit.loft_heat(spec["along"], spec["across"]), BLAST_BANDS, depth=spec["depth"], segments=10,
                    tongues=(2.5, 0.025, 1.9), gap=0.14, width_gap=0.6)
    parts = [body.build(name + "_fire", fire)]
    behind, core_length, w, lift = spec["core"]
    cmats = kit.materials("blast_core", BLAST_CORE_BANDS, kit.CORE_ROUGHNESS)
    parts.append(kit.core(name + "_core", spec["x"], spec["nose"] - behind * length, core_length * length, w, lift,
                          body.top, BLAST_CORE_BANDS, cmats, cap=0.4, taper=0.85))
    return parts


MODELS = {  # name: (sprites, what it is, its hot point (model coordinates))
    "shot_special_ball_127": ((127, 129), "the steel ball flashing: a highlight, a bright crescent", (-2.0, 1.5)),
    "shot_special_ball_128": ((128,), "the same brighter still", (-2.0, 1.5)),
    "shot_special_blast": ((49,), "a teardrop of fire, a white head", (-0.5, 3.0)),
}


def build_model(name):
    if name in BALLS:
        return steel_ball(name, BALLS[name][0])
    return blast(name)


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    for name, (sprites, what, hot) in MODELS.items():
        if only is not None and name not in only:
            continue
        k.reset()
        parts = triangulate(build_model(name))
        bpy.context.view_layer.update()
        print(f"== {name} (shots {' '.join(str(x) for x in sprites)}): {what}")
        if "check" in options:
            kit.check_lines(name, parts, os.path.join(options["check"], "shots.png"), [(x, 0, 0, 0) for x in sprites],
                            hot)
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            view(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
