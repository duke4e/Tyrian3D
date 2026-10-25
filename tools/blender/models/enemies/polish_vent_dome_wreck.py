"""The vent dome's wreck (sheet D sprite 241's stand-in: what AST ROCK's and ASTEROID?'s maps paint where vent_dome
stands once it is destroyed, before it comes and where none comes; 13 of them), built on polish_vent_dome.py and
polish_green_lamp_bunker_wreck.py (2026-10-25, the clean ground's stage 4).

As the maps paint it at 4x (AST ROCK c2523f4e40152e95 at 492, 1863): the same painting, pixel for pixel, as the grey
sentry post's wreck (green_lamp_bunker_wreck: the asteroid tiles' wreck of S 277, whose pixels D 241 is in good part):
the head's ends still standing, its middle blown out into a red-glowing hollow; the shield split down its middle, its
left half peeled out with red inside it, its right half crumpled into a grey heap; the pipes torn away (stubs along the
ground); soot round it. So the wreck is the post's wreck (polish_green_lamp_bunker_wreck.build(), its blast, embers,
split shield, pipe stubs, plates and rubble, its materials), with the vent dome's own parts: its head (the plate
between two seams where the post has its visor: the plate gone with the blasted middle, the seams' ends left) and its
crescent vent round the shield's foot, cooled and broken: the trough's left part (under the peeled half) still dull
red (mostly 0x70, its middle 0x71-0x72 glowing 0.1-0.3), its middle torn out, its right end crushed down under the crumpled half and burnt
dark.

The same frame as vent_dome: origin at the sprite's centre (pixel 12, 14), +Y up the sprite, +Z up from the ground
(z = 0); origin flag as the live line. models.cfg: model vent_dome_wreck enemies/vent_dome_wreck.glb origin;
wreck d 241 vent_dome_wreck (drawn with sprite d 241's options, yaw=0 height=-4; its glow is the live enemy's only).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>.
"""
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_green_lamp_bunker_wreck as post  # noqa: E402
import polish_vent_dome as live  # noqa: E402

NAME = "vent_dome_wreck"
# The vent cooled: its bands of heat (lowest heat, palette index, glow), duller than the live 241's.
COOLED = [(-9.0, 0x70, 0.0), (0.5, 0x71, 0.1), (0.8, 0x72, 0.2)]
# The vent broken: cut by planes x = a (the part right of LEFT_END dropped from the left piece; the right piece from
# RIGHT_START on, pressed down by SINK and turned about y by TILT degrees round its inner end).
LEFT_END, RIGHT_START, SINK, TILT = -3.4, 4.2, 0.45, 9.0


def vent_head(m):
    """The vent dome's head (polish_vent_dome.head(): a plate between two seams instead of the post's visor); the
    plate lay where the blast goes through the middle, so it goes with it."""
    m.setdefault("plate", k.material("ventdome_plate", palette=0x09, metallic=0.25, roughness=0.45))
    live.head(m)
    plate = bpy.data.objects["plate"]
    data = plate.data
    bpy.data.objects.remove(plate)
    bpy.data.meshes.remove(data)


def broken_vent(burnt):
    """The crescent vent, cooled, its middle torn out: the left part where it was, the right end crushed down and
    burnt dark. (At most 15 materials a model: its dark red and its hottest band are the post's wreck's cinder and
    ember.)"""
    m = live.materials(COOLED)
    vent = live.vent(m)
    mk.apply(vent)
    same = {"ventdome_rim@112": "lampwreck_cinder@112", "ventdome_heat_70@112": "lampwreck_cinder@112",
            "ventdome_heat_72@114": "lampwreck_ember_72@114"}
    for i, mt in enumerate(vent.data.materials):
        if mt.name in same:
            vent.data.materials[i] = bpy.data.materials[same[mt.name]]
    right = post.wk.split_piece(vent, (RIGHT_START, 0, 0), (1, 0, 0), burnt, "vent_right")
    middle = post.wk.split_piece(vent, (LEFT_END, 0, 0), (1, 0, 0), burnt, "vent_middle")
    if middle is not None:
        bpy.data.objects.remove(middle)
    if right is not None:
        for i, mt in enumerate(right.data.materials):
            if mt.name.startswith(("ventdome_heat", "lampwreck_cinder", "lampwreck_ember")):
                right.data.materials[i] = burnt
        post.wk.turn([right], (RIGHT_START, 0.0, 0.0), (0, 1, 0), TILT)
        right.data.transform(Matrix.Translation((0.0, 0.0, -SINK)))
    for obj in (vent, right):
        if obj is not None:
            k.smooth(obj, 50)


def build():
    real_head, real_finish = post.live.head, post.wk.finish

    def finish(name, options, check_top):
        broken_vent(bpy.data.materials["lampwreck_burnt@2"])
        post.wk.clip_below(mk.meshes())
        return real_finish(NAME, options, None)
    post.live.head, post.wk.finish = vent_head, finish
    try:
        post.build()
    finally:
        post.live.head, post.wk.finish = real_head, real_finish


if __name__ == "__main__":
    build()
