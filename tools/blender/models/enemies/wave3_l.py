"""Wave 3, batch L of the enemy models: the remaining enemies of sheet 5 (episode 4), authored as their sprites
look (models.cfg: yaw=0 unless noted; the stinger, 5 207: polish_flesh_stinger.py; HARVEST's purple machine, 5 3:
polish_purple_beacon.py; the hanging pod, 5 170: polish_hanging_pod.py; BRAINIAC's eye hatch, 5 164:
polish_eye_hatch.py; its stone fists, 5 81 and 83: polish_stone_fist.py; the green arrows, 5 247 and 266:
polish_green_arrow.py). What is left here are the objects drawn from several sprites, in wave3_l_parts.py; the
pixel art in wave3_l_art.py. (EYESPY's ears, 5 245 and 5 284: polish_ears.py; APPROACH's tan fighter, 5 49:
polish_tan_fighter.py.)

usage: blender -b --factory-startup -P wave3_l.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
       blender -b --factory-startup -P wave3_l.py -- --whole <prefix> [--only object] [--check 1]
--preview renders <prefix><name>_top.png and _3q.png for each model; --check prints each model's
silhouette overlap with its sprite; --whole renders the objects the game draws in pieces, whole.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_l_kit as w  # noqa: E402
import wave3_l_parts as parts  # noqa: E402
from wave3_l_kit import model  # noqa: E402


# --- The objects drawn in pieces (wave3_l_parts.py) ---------------------------------------------

for _name, _sprite, _builder in parts.PIECES:
    model(_name, _sprite)(_builder)

w.main()
