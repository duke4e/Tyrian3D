"""BUBBLES' boiling bubbles (sheet E sprite 155, 2x2: 24 x 25 pixels in the 24 x 28 cell; ground layer, enemies 465
and 467 of episode 1, 21 of them in BUBBLES; their animation 155 157 159 161 163 165 163 161 159 157 155 plays when
they fire: the cluster heats from dark red to yellow and cools again), polished (2026-10-21; it replaces wave3_aa.py's
bubbles_hot(), seven spheres painted pixel by pixel). models.cfg: model bubbles_hot enemies/bubbles_hot.glb
(unchanged) and model bubbles_hot_157 ... bubbles_hot_165 (new); sprite e 155 bubbles_hot yaw=0 glow=22:0.3
(unchanged); frame e 157 bubbles_hot_157 ... frame e 165 bubbles_hot_165. No other enemy (launched ones included)
shows E 155-165.

E 155 is E 153 (the brick-red blister cluster that does not boil, polish_bubbles.py) red hot: its coverage exactly,
its pixels in the fire ramp 7 instead of ramp 4, shade for shade (a few highlights one or two shades lower). The
frames after it are the same pixels posterised brighter: every frame maps E 153's shades the same way (153's 0x42 /
0x43 / 0x44-0x46 / 0x47 / 0x48-0x4d, the creases, the grooves, the cushions, the first highlight and the highlights,
become 157: 0x74 / 0x75 / 0x77 / 0x78 / 0x79-0x7d, 159: 0x77 / 0x77 / 0x78 / 0x79 / 0x7a-0x7e, 161: 0x78 / 0x78 /
0x79 / 0x7a / 0x7c-0x1f, 163: 0x79 / 0x79 / 0x7a / 0x7c / 0x7d-0xff, 165: 0x7a / 0x7a / 0x7c / 0x7d / 0x7e-0xff),
so the 4x upscales draw one molten cluster glowing hotter, glossy, its raised middles the brightest.

So this is polish_bubbles.py's cluster, built by it (its parts, their layout, profiles, creases and grooves, the
same mesh: the two models match): each of its five colours (pad, rim, side, groove, crease) takes the frame's shade
of ramp 7 for it, and the raised middles of the cushions and domes (the pad profile's middle, the domes' tops, the
pill's pad and ridge: the faces inside a ring of their lofts, so a ring is the border) a sixth, the hottest, the
frame's shade of E 153's 0x48; glossy (roughness 0.36) and glowing in their own colours, well under 1 (frame 155:
0.05 the creases to 0.3 the hot middles, each later frame 0.04 more, 165: 0.25 to 0.5; the game's bloom and the
sprite line's glow add to them). One model per frame: the same mesh (so the same bounds), its six materials swapped.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera; the cluster stands on z = 0
(the game centres ground models in height on the ground enemies' layer, as it does the cluster of E 153).

Replaces wave3_aa.py's bubbles_hot(): remove its section ("# --- E 155: the boiling bubbles": BUBBLES, BUBBLE_LAYOUT
and bubbles_hot() with its @kit.model("bubbles_hot", ...) registration) and the bubbles_hot lines of its docstring;
wave3_aa_art.py's BUBBLES_HOT is read by nothing else (and wave3_aa.py's import of sh from wave3_aa_kit is then unused).
Nothing imports wave3_aa.py.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against its sprite in enemy_E.png), --preview <prefix>, --only <name,...>.
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_bubbles as pb  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The frames: model, sprite, the palette index of each colour (polish_bubbles' five, the frame's shades of E 153's 0x42,
# 0x43, 0x44, 0x45 and 0x46, and the hot middles, its shade of 0x48).
KEYS = ("crease", "groove", "side", "rim", "pad", "core")
FRAMES = [
    ("bubbles_hot", 155, (0x72, 0x73, 0x74, 0x75, 0x76, 0x78)),
    ("bubbles_hot_157", 157, (0x74, 0x75, 0x77, 0x77, 0x77, 0x79)),
    ("bubbles_hot_159", 159, (0x77, 0x77, 0x78, 0x78, 0x78, 0x7a)),
    ("bubbles_hot_161", 161, (0x78, 0x78, 0x79, 0x79, 0x79, 0x7c)),
    ("bubbles_hot_163", 163, (0x79, 0x79, 0x7a, 0x7a, 0x7a, 0x7d)),
    ("bubbles_hot_165", 165, (0x7a, 0x7a, 0x7c, 0x7c, 0x7c, 0x7e)),
]
# Emission strengths of the colours in the coolest frame (in their own colours), and how much more each hotter frame
# glows (165: 0.25-0.5).
GLOW = {"crease": 0.05, "groove": 0.08, "side": 0.12, "rim": 0.16, "pad": 0.2, "core": 0.3}
GLOW_STEP = 0.04
ROUGHNESS = 0.36
# The hot middles: the faces of the pad and dome profiles whose middles lie inside this plan radius (0 the middle, 1
# the outline): the pad profile's inside its ring at 0.51, the dome's inside its ring at 0.58 (so a ring is the border).
HOT_CORE = {"pad": 0.5, "dome": 0.57, "tray": None}


def materials(name, indices, step):
    pal = k.level_palette()
    return {key: k.material(f"{name}_{key}", palette=index, metallic=0.0, roughness=ROUGHNESS, emission=pal[index],
                            emission_strength=GLOW[key] + GLOW_STEP * step)
            for key, index in zip(KEYS, indices)}


def key_of(mat):
    return mat.name.split("@")[0].rsplit("_", 1)[1]


def hot_middles(objects, parts, core_mat):
    """Gives the raised middles of the cushions and domes (the faces of their pad colour inside the plan radius
    HOT_CORE of their part, which falls between two of the lofts' rings: the border is a ring) the core colour."""
    for obj, part in zip(objects, parts):
        limit = HOT_CORE[part.kind]
        if limit is None:
            continue
        slot = mk.slot_of(obj, core_mat)
        pad = [i for i, m in enumerate(obj.data.materials) if m is not None and key_of(m) == "pad"]
        for poly in obj.data.polygons:
            if poly.material_index in pad and part.surface_r(poly.center) < limit:
                poly.material_index = slot
        obj.data.update()


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    first = materials(FRAMES[0][0], FRAMES[0][2], 0)
    objects = pb.build_cluster(first)
    hot_middles(objects, [pb.Part(*p) for p in pb.PARTS], first["core"])
    triangulate(objects)
    bpy.context.view_layer.update()
    for step, (name, sprite, indices) in enumerate(FRAMES):
        mats = first if step == 0 else materials(name, indices, step)
        for obj in objects:
            for i, m in enumerate(obj.data.materials):
                obj.data.materials[i] = mats[key_of(m)]
        if only and name not in only:
            continue
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_E.png")
            mk.compare("%s (E %d)" % (name, sprite), mk.coverage(objects, 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, objects, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, objects)


if __name__ == "__main__":
    build()
