"""The wrecks of DELI's long blue cannons on the top layer (sheet C; their stand-ins: what DELIANI's background 3 map
1e524e1fa31872b1 paints where the cannons ride, before they come and once they are destroyed: pointing right 6 places of
C 269 271 273, pointing left 4 of C 239 241 243), built on polish_deli_cannon_dmg.py (2026-10-25, the clean ground's
stage 5: the top enemies riding background 3).

As the map paints it (its tiles at 4x in the HD tiles): only the mount is left, and it is the damaged look's mount
(C 233; pointing left C 279) pixel for pixel, its black (0x01) painted in the darkest blue (0x31), drawn lower down the
screen than the live piece: 2 to 4 pixels (3 at most places; the riders' logged places jitter by a pixel or two) — the
mount fallen off its platform's edge onto the floor, the breech, the barrel and the muzzle gone (where they were the map
paints the purple platform and the grey machinery under them). So only the mounts get wrecks; models.cfg:
model deli_cannon_mount_wreck enemies/deli_cannon_mount_wreck.glb origin,
model deli_cannon_l_mount_wreck enemies/deli_cannon_l_mount_wreck.glb origin;
wreck c 271 deli_cannon_mount_wreck, wreck c 241 deli_cannon_l_mount_wreck (drawn with the live sprite lines' options:
yaw=0 height=-6); and nothing for the other pieces: wreck c 269 none, wreck c 273 none, wreck c 275 none, wreck c 238
none, wreck c 239 none, wreck c 243 none.

The model: polish_deli_cannon_dmg.py's damaged cannon (its parts, damage and materials; built whole and leaned by
polish_deli_cannon.build_whole, mirrored for the left one) cut to the mount's box as the live and damaged mounts are
(polish_deli_cannon.pieces_of), the black of its burns, slots and cuts repainted the darkest blue (0x31) as painted, every blue two shades darker
(the painting reads darker than the damaged model: the sprite's black outlines are dark blue in it), its
cracks' embers dimmed as they die down (0x74 at 0.26, 0x76 at 0.34, the dying 0x72 at 0.12: the damaged look's are 0.35,
0.5 and 0.15), and moved PAINT_DY down the screen to where the painting lies.

Coordinates as polish_deli_cannon.py's pieces: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the
platform (z = 0); origin at the mount sprite's middle (models.cfg origin).

Options after "--": --outdir <dir> (default assets/models/enemies), --preview <prefix>, --only <name,...>.
"""
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
import polish_deli_cannon as cn  # noqa: E402
import polish_deli_cannon_dmg as cnd  # noqa: E402

PAINT_DY = -3.0                # the painting lies this much lower down the screen than the live mount (2-4 px)
# (name, the live piece it stands in for, mirrored: pointing left)
PIECES = [("deli_cannon_mount_wreck", "deli_cannon_mount", False),
          ("deli_cannon_l_mount_wreck", "deli_cannon_l_mount", True)]
# Every blue one step (two shades) darker: the painting's mount reads darker than the damaged look's model (its black
# outlines and burns are the darkest blue there).
DARKER = {"b2": "b1", "b4": "b2", "b6": "b4", "b8": "b6", "ba": "b8", "bc": "ba", "be": "bc"}
EMBERS = {"ember": (0x74, 0.26), "ember_hot": (0x76, 0.34), "ember_dim": (0x72, 0.12)}


def materials():
    m = cnd.materials()
    pal = k.level_palette()
    m["b1"] = k.material("dcanw_blue1", palette=0x31, metallic=0.18, roughness=0.5)
    for key, (index, glow) in EMBERS.items():
        m[key + "_w"] = k.material("dcanw_" + key, palette=index, metallic=0.0, roughness=0.5, emission=pal[index],
                                   emission_strength=glow)
    return m


def repaint(objects, m):
    """The black (the burns' char, the slots' and cuts' seams) the darkest blue, every blue a step darker, the embers
    dimmed."""
    swap = {m["char"].name: m["b1"], m["seam"].name: m["b1"]}
    for key, darker in DARKER.items():
        swap[m[key].name] = m[darker]
    for key in EMBERS:
        swap[m[key].name] = m[key + "_w"]
    for obj in objects:
        for i, mat in enumerate(obj.data.materials):
            if mat is not None and mat.name in swap:
                obj.data.materials[i] = swap[mat.name]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    for name, live, mirror in PIECES:
        if only and name not in only:
            continue
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"
        m = materials()
        whole = cn.build_whole(m, mirror, cnd.damaged_parts)
        repaint(whole, m)
        box = next(b for n, _, _, b in (cn.PIECES_L if mirror else cn.PIECES) if n == live)
        pieces = cn.pieces_of(whole, box, m["b1"])
        mk.transform(pieces, Matrix.Translation((0.0, PAINT_DY, 0.0)))
        triangulate(pieces)
        for src in whole:
            src.hide_render = True
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)


if __name__ == "__main__":
    build()
