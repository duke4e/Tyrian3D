"""Batch AR of wave 3: an object whose frames change shape, for frame lines, built by its own script's builders
(imported as they are, their output unchanged) and posed as the frames draw it (models.cfg: as its first
frame's models, yaw=0).

- gryphon_head_<sprite> (sheet 0, enemy 835, the GRYPHON's head, sprite 0 123; wave3_ai_gryphon.py): when the head
  fires, its jaw drops and closes again, 123 121 119 129 119 121 123, two pixels a frame: the lower jaw and its
  teeth slide down the screen, the maw between the fangs grows. wave3_ai_gryphon.py's head (gryphon_head) is 119;
  the builder fed the frame's pixels makes 123 (the jaw shut, the head as it is when it doesn't fire), 121 and 129
  (wide open), its lower teeth moved with the jaw.
(CORE's lava bubble's frames, 3 130 and 132: polish_lava_bubble.py; SAVARA's airship's fan, I 17, 55, 93, 131:
polish_airship.py.)

usage: Blender -b --factory-startup -P wave3_ar_beasts.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import os
import sys

import bpy
from mathutils import Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ar_kit as kit  # noqa: E402
import wave3_ar_art as art  # noqa: E402

gi = kit.quiet_import("wave3_ai_gryphon")
kit.forget()
n = kit.n
w = kit.w


def objects(prefix):
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith(prefix)]


# --- The GRYPHON's head ---------------------------------------------------------------------------------------------

def gryphon_head(sprite, drop):
    """wave3_ai_gryphon's head built from frame `sprite`'s pixels; drop: how far its jaw is lowered (pixels) from
    where 119 (the builder's) has it."""
    saved = gi.HEAD, gi.HEAD_PAINT
    gi.HEAD = gi.kit.Frame(getattr(art, f"GRYPHON_HEAD_{sprite}"), 24, (12, 14))
    gi.HEAD_PAINT = gi.kit.Frame(getattr(art, f"GRYPHON_HEAD_{sprite}"), 24, (12, 14)).fill({0x01, 0xfe})
    try:
        gi.gryphon_head()
    finally:
        gi.HEAD, gi.HEAD_PAINT = saved
    w.transform(objects("ghead_tooth"), Matrix.Translation((0.0, -drop, 0.0)))


for sprite, drop in ((123, -4.0), (121, -2.0), (129, 2.0)):
    f = gi.kit.Frame(getattr(art, f"GRYPHON_HEAD_{sprite}"), 24, (12, 14))
    n.model(f"gryphon_head_{sprite}", mask=lambda f=f: f.mask((0, 24, 0, 28)))(
        lambda sprite=sprite, drop=drop: gryphon_head(sprite, drop))


def main():
    options = kit.k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    # Each with its own script's build loop: the head's (wave3_v_kit's, as wave3_ai_gryphon builds it).
    saved = list(n.MODELS)
    try:
        n.MODELS[:] = [m for m in saved if m[0].startswith("gryphon_head")]
        if n.MODELS:
            gi.kit.v.run()
        n.MODELS[:] = [m for m in saved if not m[0].startswith("gryphon_head")]
        if n.MODELS:
            n.run()
    finally:
        n.MODELS[:] = saved


if __name__ == "__main__":
    main()
