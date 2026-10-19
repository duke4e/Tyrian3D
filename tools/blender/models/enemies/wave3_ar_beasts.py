"""Batch AR of wave 3: three objects whose frames change shape, for frame lines, built by their own scripts' builders
(imported as they are, their output unchanged) and posed as the frames draw them (models.cfg: as their first
frame's models, yaw=0).

- gryphon_head_<sprite> (sheet 0, enemy 835, the GRYPHON's head, sprite 0 123; wave3_ai_gryphon.py): when the head
  fires, its jaw drops and closes again, 123 121 119 129 119 121 123, two pixels a frame: the lower jaw and its
  teeth slide down the screen, the maw between the fangs grows. wave3_ai_gryphon.py's head (gryphon_head) is 119;
  the builder fed the frame's pixels makes 123 (the jaw shut, the head as it is when it doesn't fire), 121 and 129
  (wide open), its lower teeth moved with the jaw.
- zeppelin_<sprite> (sheet I, SAVARA's airship; wave3_k.py): its fan turns, the pieces I 3, 5, 41, 43 alternating
  with 17, 55, 93, 131. wave3_k.py's airship has two white blades in the fan's duct (40 and 140 degrees round it);
  the frames show four blades in other places (about 20, 65, 115 and 160 degrees), which the models here have
  (wave3_k's two blades turned and copied), the rest as wave3_k builds it, cut into the same pieces.
- lava_bubble_<sprite> (sheet 3, CORE's lava bubble, 3 128; wave3_n.py): it wobbles, 128 130 132 130, the bubble
  swelling a pixel (130) and the lava splashed round its foot moving (130, 132): wave3_n's bubble with the splashes
  where those frames draw them (its builder fed their pixels), swollen for 130.

usage: Blender -b --factory-startup -P wave3_ar_beasts.py -- [--only names] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_ar_kit as kit  # noqa: E402
import wave3_ar_art as art  # noqa: E402

gi = kit.quiet_import("wave3_ai_gryphon")
nb = kit.quiet_import("wave3_n")
zk = kit.quiet_import("wave3_k")
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


# --- SAVARA's airship: its fan ---------------------------------------------------------------------------------------

def zeppelin_fan():
    """wave3_k's airship with its fan turned: its two blades (40 and 140 degrees round the duct's axis) turned and
    copied to four (20, 65, 115 and 160 degrees)."""
    zk.zeppelin_whole()
    t = math.radians(35.0)       # the duct's lean and centre, as wave3_k builds it
    centre = Vector((zk.ZX, 37.0, 17.5))
    axis = Vector((0, -math.sin(t), math.cos(t)))
    hub = centre - axis * 1.2
    for name, turns in (("blade40", (-20.0, 25.0)), ("blade140", (-25.0, 20.0))):
        blade = bpy.data.objects[name]
        copy = blade.copy()
        copy.data = blade.data.copy()
        copy.name = name + "_copy"
        bpy.context.scene.collection.objects.link(copy)
        for obj, deg in zip((blade, copy), turns):
            obj.data.transform(kit.about(hub, Matrix.Rotation(math.radians(deg), 4, axis)))


# Same boxes as I 3, 5, 41 and 43 (wave3_k.ZEPPELIN_PIECES).
ZEP_FRAMES = {3: 17, 5: 55, 41: 93, 43: 131}
ZEP_PIECES = [(ZEP_FRAMES[s], x0, x1, y0, y1) for s, x0, x1, y0, y1 in zk.ZEPPELIN_PIECES if s in ZEP_FRAMES]


# --- CORE's lava bubble --------------------------------------------------------------------------------------------

def lava_bubble(sprite, swell):
    """wave3_n's lava bubble with the splashes round its foot where frame `sprite` draws them (its builder fed the
    frame's pixels), the bubble swollen by `swell` (taller, its top a little further up the screen)."""
    saved = nb.art.DOME
    nb.art.DOME = getattr(art, f"LAVA_{sprite}")
    try:
        nb.lava_bubble()
    finally:
        nb.art.DOME = saved
    if swell:
        foot = 1.6 - 9.4          # the bubble's south edge (cy - ry, as wave3_n builds it)
        grow = Matrix.Translation((0.0, foot, 0.0)) @ Matrix.Diagonal((1.0, 1.0 + swell * 0.45, 1.0 + swell, 1.0)) @ \
            Matrix.Translation((0.0, -foot, 0.0))
        w.transform([bpy.data.objects["dome"], bpy.data.objects["lip"]], grow)


for sprite, swell in ((130, 0.12), (132, 0.0)):
    n.model(f"lava_bubble_{sprite}", mask=lambda sprite=sprite: kit.sheet_mask("enemy_3", sprite))(
        lambda sprite=sprite, swell=swell: lava_bubble(sprite, swell))


def main():
    options = kit.k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    # Each with its own script's build loop: the head's (wave3_v_kit's, as wave3_ai_gryphon builds it), the bunker's
    # and the bubble's (wave3_n_kit's, as wave3_n builds them).
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
    names = {f"zeppelin_{p[0]}" for p in ZEP_PIECES}
    if not only or "zeppelin" in only or names & only:
        zk.OBJECTS = {"zeppelin": (zeppelin_fan, (96, 140), "enemy_I", ZEP_PIECES, ())}
        zk.main()


if __name__ == "__main__":
    main()
