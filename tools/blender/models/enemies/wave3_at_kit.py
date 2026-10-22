"""Helpers for batch AT of wave 3, the second animation pass: models for the animation frames the earlier scripts left
static (their docstrings say which), for models.cfg's frame lines (frame <sheet> <sprite> <model>: while an enemy shows
that frame, the game draws that model in the place and with the options of the sprite line's model). As in batch AR
(wave3_ar_kit.py, whose helpers this re-exports), each object is built by its own script's builder (imported as it is,
quiet_import: its output stays unchanged), posed as the frame draws it and cut exactly as the static piece is.

The scripts: wave3_at_j.py (sheet J: the green shell's lids, the eye orb); the other frames' models are the polish
scripts' (the bladed orange's polish_orange_saw.py's, the armoured dome's gun port polish_armour_dome.py's, MINERS's
rig's hatch and drill polish_miners_rig.py's, the tan creature's nub polish_tan_dome.py's, CORAL's manta
polish_coral_manta.py's, the eye tub's iris polish_eye_tub.py's, the shell ship polish_shell_ship.py's, the eye hatch's
lids polish_eye_hatch.py's, the core in the pipe cage polish_maze_pipe.py's, the drill's arm polish_ice_drill.py's).
The frames' sprites are read from the extracted sheets for --check (sheet_mask) only: the poses are set by hand from
the frames' pixels (each script says which).

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera).
"""
import os
import sys

import bpy  # noqa: F401
from mathutils import Matrix, Vector  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from wave3_ar_kit import *  # noqa: E402,F401,F403
import wave3_ar_kit as ar  # noqa: E402,F401
from wave3_ar_kit import k, w, n, pal, paint_faces  # noqa: E402,F401

quiet_import = ar.quiet_import
forget = ar.forget


def objects(prefix):
    """The scene's meshes whose names start with prefix (a string or a tuple of them)."""
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith(prefix)]


def remove(names):
    """Removes the named objects (those that exist)."""
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            bpy.data.objects.remove(obj)
