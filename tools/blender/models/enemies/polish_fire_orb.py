"""The glowing orange orb of ** ALE **, SOH JIN, MISTAKES and APPROACH (sheet A sprite 277, 2x2: an 18 x 17 ball in the
24 x 28 cell; enemy 841 on the top layer in ** ALE **, enemy 779 on the ground in the others, about 35 of them; its
animation pulses it darker and back, three game frames each: 277 239 201 199 201 239), polished (2026-10-19; it
replaces wave1_b.py's fire_orb(), an ellipsoid in four bands of height). models.cfg: sprite a 277 fire_orb yaw=0
glow, frame a 239 fire_orb_239, frame a 201 fire_orb_201, frame a 199 fire_orb_199. No other enemy shows these four
sprites.

A 277 is M 115's pixels (polish_balls.py's glossy ball, also A 279) in the fire ramp (7) instead of the blue (3), shade
for shade, and its darker frames are the dark ball's frames in ramp 7, shade for shade: A 239 is A 241
(ball_dark_241), A 201 is A 203 (ball_dark_203), A 199 is A 165 (ball_dark; its two near-black outline pixels in ramp
13 instead of 9). So the fire orb is that ball, not modelled again: this script builds polish_balls' painted ball for
each frame (its white glare above the middle on the left, the bright crescent inside the rim at the lower right
where the light gathers as in a marble, the dark rim), every palette material moved to ramp 7 and, as the orb
glows, glowing in its own palette colour (GLOW: the rim a dull red, the body orange, the glare and the crescent
hot). (models.cfg's color=sprite on the ball models would show the same colours without models of their own, but
without the glow: the ball's materials have no coloured emission, which would not follow the frame's ramp.)

As polish_balls' ball: origin at the sprite's centre (pixel 12, 14); +Y up the screen, +Z towards the camera; the
orb's middle at (0, 0.5), standing on z = 0. All four frames span the same bounds, so the game, which centres them
in height on their layer, keeps them in place.

Replaces wave1_b.py's fire_orb() (its MODELS entry; it was the file's last model): remove it so that it doesn't
overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against its sprite in enemy_A.png), --preview <prefix>, --only <name,...>.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_balls import BALL, BALL_FRAMES, RIM_DARK, WHITE, ball_paint, painted_ball, preview, triangles  # noqa: E402

RAMP = 7
# The frames: (model, sprite, polish_balls' frame of the same pixels).
FRAMES = [("fire_orb", 277, "ball"), ("fire_orb_239", 239, "ball_dark_241"), ("fire_orb_201", 201, "ball_dark_203"),
          ("fire_orb_199", 199, "ball_dark")]
# How far each part glows in its own palette colour (the darker frames' colours are darker, so they glow less), and
# its finish. The body keeps the sprite's shade (the ball lifts it a shade for the side its sun doesn't reach; the
# glow does that here). The crescent glows in white over its own colour, as the ball's.
GLOW = {"body": 0.42, "rim": 0.5, "glare": 0.7, "glare_mid": 0.9, "glare_core": 1.1, "crescent": 0.8,
        "crescent_core": 1.25}
CRESCENT_WHITE = (0.12, 0.3)
FINISH = {"body": dict(metallic=0.0, roughness=0.22), "rim": dict(metallic=0.0, roughness=0.45)}


def materials(name, body, glare, crescent):
    """polish_balls.ball_materials' shades in ramp 7, each glowing in its own colour."""
    pal = k.level_palette()
    shades = {"body": body, "rim": max(0, body - RIM_DARK), "glare": glare[0], "glare_mid": glare[1],
              "glare_core": glare[2], "crescent": crescent[0], "crescent_core": crescent[1]}
    out = {}
    for key, shade in shades.items():
        index = 16 * RAMP + shade
        finish = FINISH.get(key, dict(metallic=0.0, roughness=0.15))
        colour = pal[index]
        if key.startswith("crescent"):  # the light gathered in it: its colour lifted towards white
            mix = CRESCENT_WHITE[key == "crescent_core"]
            colour = tuple(round(c + (w - c) * mix) for c, w in zip(colour, WHITE))
        out[key] = k.material(f"{name}_{key}", palette=index, emission=colour, emission_strength=GLOW[key], **finish)
    return out


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = set(options["only"].split(",")) if "only" in options else None
    balls = {row[0]: row for row in BALL_FRAMES}
    for name, sprite, ball_name in FRAMES:
        if only is not None and name not in only:
            continue
        _, _, body, glare, glare_scale, crescent, crescent_scale = balls[ball_name]
        k.reset()
        painted_ball(name, BALL, ball_paint(glare_scale, crescent_scale), materials(name, body, glare, crescent))
        used = {m.name for obj in bpy.context.scene.objects if obj.type == "MESH" for m in obj.data.materials}
        print("== %s (A %d, as %s): %d triangles, %d materials: %s" % (name, sprite, ball_name, triangles(), len(used),
                                                                       ", ".join(sorted(used))))
        if "check" in options:
            k.check_silhouette(os.path.join(options["check"], "enemy_A.png"), sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %d bytes" % (path, os.path.getsize(path)))
        if "preview" in options:
            preview(options["preview"] + name)


if __name__ == "__main__":
    build()
