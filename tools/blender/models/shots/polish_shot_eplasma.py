"""The enemies' blue plasma ball (shots sheet 2 sprites 2, 3 and 4, 502-504 in the game, all 1x1: 12 x 14 cells),
modelled (2026-10-30, round 3 of the energy shots' models; until then it was drawn as its sprite with volume, flat,
from the 4x sheets, with the automatic glow).

Who fires it: enemy weapon 48 in episodes 4 and 5 (drain 10, shotrepeat 1, aimed at the player: aim 5), once Enemy
Fire Override events give the turrets a frequency: ASTEROIDS' rocks (enemy 1143) and CORAL's (1224, 1225); also weapon
817 (the same ball, two frames), which no enemy of the levels fires. An enemy's shot shows weapani frames (tyrian2.c:
animate cycles below animax = weapani, one step a game frame): weapon 48 has weapani 3, so the ball shows shots2 2, 3
and 4 by turns, growing and starting again (it throbs, 35 times a second). Round, aimed every way: its lines take no
yaw.

As the sprites draw it: a ball of plasma, all three frames round the same middle (columns 5 and 6, rows 5 and 6 of the
cell: the cell's centre column, a pixel above its centre row), 2 (6 pixels across) a white middle two pixels wide
(0xdf), light blue round it (0x9f, 0x9c), its rim blue (0x99, 0x9b); 3 (8 across) and 4 (10 across) the same with a
larger white middle (four and six pixels: 0xdf, ramp 13's white, edged with ramp 8's pale cyan 0x8c, 0x8d on its
diagonals), light blue (0x9d-0x9f) round it, a blue rim (0x98-0x9a; 4's corners 0x96).

The model: polish_shot_pellet.py's bead (a dome round on top and flat underneath, its bands on rings of the mesh, the
borders waving round it a little, a heart standing out of its top, leant towards the camera so that the camera sees the
rings where the sprite lays them out) as a ball of plasma 10 pixels across, 4's look: ramp 9's blues out from a white
heart (0xdf round which pale cyan 0x8d, standing 0.5 pixels proud) through light blue (0x9e, 0x9c) to a blue rim
(0x99, a shade under the sprite's 0x99-0x9a rim at its edge: 0x97), every band glowing (0.38-0.6, the heart 0.62), so
the ball reads bright all over from the slanted camera (a ball lit only by the sun reads near black on its far side).
The frames only grow (the white middle a little smaller in the smaller ones): one model, shown at scale=0.6 (2) and 0.8
(3) and moved onto the sprites' middle with at=0:-1 (a pixel up the screen; the ball is built round the origin, so the
scale keeps it there). 588 triangles, 6 materials.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the ball's middle
on the origin (its lines move it onto the sprites': at=0:-1); it stands on z = 0 (the game centres shot models in
height on the player's layer).

models.cfg (the shots section):
    model shot_eplasma shots/shot_eplasma.glb
    shot shots2 2 shot_eplasma at=0:-1 scale=0.6 glow=...
    shot shots2 3 shot_eplasma at=0:-1 scale=0.8 glow=...
    shot shots2 4 shot_eplasma at=0:-1           glow=...

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_eplasma.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (the model at each frame's scale and at=
     against the frames in <dir>/shots2.png, from TYR3D_EXTRACT) [--preview <prefix>] (top, three-quarter and
     game-camera views)
"""
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ENEMIES = os.path.join(HERE, "..", "enemies")
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, ENEMIES)
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import check_frames  # noqa: E402
from polish_shot_pellet import Bead, bead, materials, OUTDIR  # noqa: E402
from polish_shot_pulse import game_view  # noqa: E402

# The heat out from the middle (u = r / 5), in shades (16: white): 4's white out to 2.6 pixels, its pale cyan edge
# (0x8d, 15) at ~2.9, light blue (0x9e) at 3.5, 0x9c at 3.8, the rim (0x99, 0x96) at 4.5-4.7.
HEAT = ((0.0, 16.0), (0.5, 16.0), (0.58, 15.0), (0.7, 14.0), (0.77, 12.0), (0.9, 9.5), (1.0, 7.0))
RADIUS, HEIGHT = 5.0, 3.8
# Its bands ((lowest heat, palette index, emission), the rim first) and its heart's ((from u, palette index, emission),
# the middle first).
BANDS = [(-99.0, 0x97, 0.38), (9.0, 0x99, 0.46), (11.0, 0x9c, 0.56), (13.0, 0x9e, 0.6)]
HEART_BANDS = ((0.0, 0xdf, 0.62), (0.62, 0x8d, 0.6))
HEART = (2.9, 0.5)  # (radius, how far it stands proud of the ball's top)
FLAMES = (6, 0.03, 1.7, 0.1)  # (lobes round it, their reach in u, their turn per border, their swell in pixels)
PLASMA_ROUGHNESS, HEART_ROUGHNESS = 0.45, 0.4

# The frames: sprite (on the second sheet): scale (its width against 4's 10 pixels); every frame's middle a pixel above
# the cell's centre (at=0:-1).
FRAMES = {2: 0.6, 3: 0.8, 4: 1.0}
AT = (0.0, -1.0)
MODELS = [
    ("shot_eplasma", 4, "the blue plasma ball (shots2 2 and 3, the smaller frames: scale=0.6, 0.8)"),
]


def build_model(name, sprite):
    spec = Bead(0.0, 0.0, RADIUS, HEIGHT, HEAT, BANDS, (HEART[0] / RADIUS, HEART[0] / RADIUS, HEART[1], HEART_BANDS),
                flames=FLAMES, segments=32, heart_segments=14, heart_rings=(0.35, 0.65, 0.88, 1.0))
    return triangulate(bead(name, spec, materials("eplasma", spec.bands, PLASMA_ROUGHNESS),
                            materials("eplasma_heart", spec.heart[3], HEART_ROUGHNESS)))


def frame_matrix(sprite):
    """The model as its line shows it in the cell: sized, moved onto the sprite's middle (at=, dy down the screen)."""
    return Matrix.Translation((AT[0], -AT[1], 0.0)) @ Matrix.Scale(FRAMES[sprite], 4)


def cfg_lines():
    return ["model shot_eplasma shots/shot_eplasma.glb"] + [
        f"shot shots2 {s} shot_eplasma at=0:-1" + (f" scale={FRAMES[s]:g}" if FRAMES[s] != 1.0 else "")
        for s in sorted(FRAMES)]


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    for name, sprite, what in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts = build_model(name, sprite)
        bpy.context.view_layer.update()
        print(f"== {name} (shots2 {sprite}): {what}")
        if "check" in options:
            check_frames(parts, os.path.join(options["check"], "shots2.png"),
                         [(s, frame_matrix(s), f"shots2 {s}") for s in sorted(FRAMES)], move_to_frame=False)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            game_view(options["preview"] + name, parts)
    print("CFG:")
    for line in cfg_lines():
        print(line)


if __name__ == "__main__":
    build()
