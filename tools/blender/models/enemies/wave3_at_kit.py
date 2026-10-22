"""Helpers for batch AT of wave 3, the second animation pass: models for the animation frames the earlier scripts left
static (their docstrings say which), for models.cfg's frame lines (frame <sheet> <sprite> <model>: while an enemy shows
that frame, the game draws that model in the place and with the options of the sprite line's model). As in batch AR
(wave3_ar_kit.py, whose helpers this re-exports), each object is built by its own script's builder (imported as it is,
quiet_import: its output stays unchanged), posed as the frame draws it and cut exactly as the static piece is.

The scripts (the bladed orange's frames are polish_orange_saw.py's): wave3_at_m.py (sheet M: the armoured dome's gun port, the
rig's hatch) (CORAL's manta, sheet T: polish_coral_manta.py),
wave3_at_d.py (sheet D: the eye tub's iris, the shell ship), wave3_at_j.py (sheet J: the green shell's lids, the eye
orb), wave3_at_misc.py (sheets 7, L: the drill's arm, the tan creature's nub; the eye hatch's lids are
polish_eye_hatch.py's, the core in the pipe cage polish_maze_pipe.py's). The frames' sprites are read from the
extracted sheets for --check (sheet_mask) only: the poses are set by hand from the frames' pixels (each script says
which).

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


def fire_mats(prefix, heat):
    """Five glowing fire materials, from the dark red of its flanks to its white-hot core; heat (0-1) brightens
    them (a dull ember at 0, a blazing ball at 1)."""
    hot = int(round(2 * heat))
    shades = [0x73 + hot // 2, 0x75 + hot // 2, 0x77 + hot // 2, 0x79 + hot, 0x7b + hot]
    glows = [0.5, 0.8, 1.1, 1.5, 2.0]
    return [pal(f"{prefix}_fire{i}", s_, metallic=0.0, roughness=0.35, glow=g * (0.7 + 0.6 * heat))
            for i, (s_, g) in enumerate(zip(shades, glows))]


def fireball(prefix, centre, radii, heat, seed=7, flames=True, core=True):
    """A lumpy ball of flame at centre (its radii (rx, ry, rz)): red at its flanks, orange and yellow over its crown,
    smaller flames bulging from it when it is big (flames), a white-hot heart (core, once it is hot)."""
    mats = fire_mats(prefix, heat)
    x, y, z = centre
    rx, ry, rz = radii

    def pick(c, nrm):
        up = nrm.z
        return mats[3] if up > 0.8 else mats[2] if up > 0.45 else mats[1] if up > 0.0 else mats[0]
    # Under 300 triangles a part, so that the build loops' triangle budget leaves them smooth.
    parts = [w.lumpy(f"{prefix}_fire", (x, y, z), (rx, ry, rz), mats[2], seed=seed, amount=0.3, segments=16,
                     rings=9)]
    if flames and min(rx, ry) > 2.6:
        for i, (ax, ay, s_) in enumerate(((-0.75, 0.35, 0.42), (0.7, -0.4, 0.38), (0.15, 0.8, 0.34),
                                          (-0.3, -0.75, 0.36))):
            parts.append(w.lumpy(f"{prefix}_flame{i}", (x + ax * rx, y + ay * ry, z - rz * 0.15),
                                 (rx * s_, ry * s_, rz * s_ * 0.9), mats[1], seed=seed + 4 + i, amount=0.3,
                                 segments=10, rings=6))
    for obj in parts:
        paint_faces(obj, pick)
    if core and heat > 0.2:
        inner = w.lumpy(f"{prefix}_fire_core", (x - rx * 0.12, y + ry * 0.18, z + rz * 0.4),
                        (rx * 0.45, ry * 0.42, rz * 0.45), mats[4], seed=seed + 1, amount=0.25, segments=12, rings=7)
        paint_faces(inner, lambda c, nrm: mats[4] if nrm.z > 0.3 else mats[3])
        parts.append(inner)
    for obj in parts:
        k.smooth(obj, 60)
    return parts
