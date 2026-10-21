"""GYGES' glossy blue bubbles with a light swirl inside (sheet n sprites 125, 15 and 13, 2x2 each: a ball 15 x 16, 17 x
18 and 19 x 21 pixels; enemies 174 and 177 (125), 175 and 178 (15), 176 and 179 (13) of episode 2, one frame each),
polished (2026-10-22, round 29; they replace wave3_an.py's bubble(), a sphere painted pixel by pixel with its swirl
embossed). models.cfg (all unchanged): model gyges_bubble_s / gyges_bubble_m / gyges_bubble_l
enemies/<name>.glb; sprite n 125 gyges_bubble_s yaw=0, sprite n 15 gyges_bubble_m yaw=0, sprite n 13 gyges_bubble_l
yaw=0. No other enemy, launched ones included, shows these sprites.

The three sprites are the asteroid levels' whorled orb, sheet M's 117, 119 and 121 (polish_balls.py's orb_whorl,
orb_whorl_119 and orb_whorl_121), pixel for pixel in other ramps: every pixel's shade is the same, ramp 3 (blue) for
the orb's ramp 5 (purple) and the outline 0x01 for its 0x21. So each bubble is that model in ramp 3 with the outline
in 0x01: polish_balls.orb_whorl() itself (a glossy ball, an icosphere cut along the borders of its painted bands: a
rounded knob above the middle on the left, a dark groove curling round it from its left, under it and up its right
side, the outer coil's lit crest round that, the dark rim; each shade a palette colour glowing 0.3 in its own colour,
so that the ball's side away from the sun, which the slanted camera sees, stays blue, not black). The orb's models
can't simply take the bubbles' colours (color=sprite): their emission would stay purple. One model per sprite, as
the orb's frames are (the bigger ones a shade or three darker with a wider dark rim, as the sprites draw them).

Where GYGES puts them (t5306-5363, as the maw boss comes in): ground enemies rolling in from both sides of the
screen, five small ones, then six middle-sized and two big ones from each (174, 175, 176 at x 18 on the ground; 177,
178, 179 at x 290 on ground 2; four to seven ticks apart), each zigzagging across (exc between -4 and 4) and rolling
down the screen a pixel a tick faster than the ground. No episode 6 level takes these waves. Models without
"origin" on the ground stand on it (the game lifts them so that nothing reaches below it), as the orbs do on the
asteroids.

Replaces wave3_an.py's bubbles (its section "# --- The bubbles": bubble() and its three registrations, and the
gyges_bubble paragraph of its docstring) and wave3_an_art.py's ORB_13, ORB_15 and ORB_125 (only that section reads
them); wave3_an_kit.py stays as it is (the boss and the pincers use it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each bubble's silhouette
against enemy_N.png), --preview <prefix>, --only <name,...>.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_balls as pb  # noqa: E402

RAMP = 3          # the bubbles' blue (the orb's 5)
OUTLINE = 0x01    # their outline (the orb's 0x21)
# (model, sprite, the orb's frame it is pixel for pixel: polish_balls.ORB_FRAMES' model name)
BUBBLES = [("gyges_bubble_s", 125, "orb_whorl"), ("gyges_bubble_m", 15, "orb_whorl_119"),
           ("gyges_bubble_l", 13, "orb_whorl_121")]


def triangulate(objects):
    """Every face a triangle (painted_ball's are already; the same split every run, the custom normals kept)."""
    for obj in objects:
        mod = obj.modifiers.new("triangulate", "TRIANGULATE")
        mod.quad_method = "BEAUTY"
        mod.ngon_method = "BEAUTY"
        mod.min_vertices = 4
        mod.keep_custom_normals = True
        mk.apply(obj)
    return objects


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_N.png") if os.path.isdir(sheets) else sheets
    frames = {f[0]: f for f in pb.ORB_FRAMES}
    pb.ORB_OUTLINE = OUTLINE
    for name, sprite, orb in BUBBLES:
        if only is not None and name not in only:
            continue
        k.reset()
        _, _, centre, radii, darker, rim_wider = frames[orb]
        pb.orb_whorl(name, centre, radii, darker, rim_wider, RAMP)
        objects = triangulate(mk.meshes())
        bpy.context.scene.view_settings.view_transform = "Standard"
        if sheet:
            mk.compare("%s (n %d)" % (name, sprite), mk.coverage(objects, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, objects, os.path.join(out, name + ".glb"))
        if "preview" in options:
            pb.preview(options["preview"] + name, distance=0.6)


if __name__ == "__main__":
    build()
