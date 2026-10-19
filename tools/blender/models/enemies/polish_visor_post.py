"""DREAD-NOT's small grey post with a glowing red visor (sheet 5 sprite 133, 1x1: 12 x 14 pixels; enemy 516 of episode
4, top layer, armour 255; not animated; the level sends rows of them up the screen, head first), polished (2026-10-19;
it replaces wave3_l.py's visor_post(), a plain lathe with a red ring). models.cfg: model visor_post
enemies/visor_post.glb; sprite 5 133 visor_post yaw=0 (unchanged).

L 134 (SQUADRON's small grey bolt, enemy 727 of episode 4, ground layer; squad_bolt, wave3_z_small.py) is this sprite
upside down, pixel for pixel (only its visor's dark end pixel differs): "sprite l 134 visor_post yaw=180 height=-1.1"
would show this model there, turned to point down the screen as L 134 does (height=-1.1: the game centres a ground
model 5.2 tall on the ground enemies' layer, 4, so its underside would float 1.4 over the ground; this sets it at 0.3).

As the sprite and its 4x upscale draw it, lying along the screen (it travels up it): a polished grey head like a
bullet (rows 1-8: a dark point, swelling to its widest at rows 3-6, lit down its left), a red visor right round it at
its widest (row 5, brightest a little left of the middle), a narrow neck (row 9) and a flared foot (rows 10-13: a lit
ring at the neck, a darker hollow, a lit rim, its flat end dark).

Built as a turned part: one profile turned about the post's axis (along y, at AXIS_Z): the point, a dark cap on it,
the head, a shallow groove round its widest part that holds the visor (a ring of red glass, glowing, hottest along
its top), the neck, the foot with a dark seam where it meets the neck and a dark end; smooth shaded, its rims kept
crisp.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen (the point's way), +Z towards the camera;
origin at the sprite's centre (pixel 6, 7): column c, row r is (c + 0.5 - 6, 6.5 - r). Lying with its underside at
z = 0 (sky and top layer models are centred in height by the game).

Replaces wave3_l.py's visor_post(): remove it with its @model("visor_post", 133, large=False) registration and its
docstring line (wave3_l_art.py's POST is not read by anything: remove it too), so that it doesn't overwrite this
model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_5.png), --preview <prefix>.
"""
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

AXIS_Z = 2.6
# The profile from the point (y, radius) to the foot's end: the point and its cap, the head, the visor's groove,
# the neck, the foot. Radii include the sprite's dark outline, a little in.
PROFILE = [(6.15, 0.0), (6.05, 0.45), (5.8, 0.9), (5.4, 1.35), (4.9, 1.8), (4.3, 2.2), (3.6, 2.45), (2.9, 2.55),
           (2.25, 2.58), (2.15, 2.4), (1.0, 2.4), (0.9, 2.58), (0.3, 2.55), (-0.4, 2.35), (-1.1, 2.0), (-1.7, 1.55),
           (-2.15, 1.05), (-2.55, 0.85), (-2.95, 0.95), (-3.3, 1.35), (-3.7, 1.75), (-4.2, 2.05), (-4.7, 2.25),
           (-5.2, 2.5), (-5.7, 2.6), (-6.2, 2.55), (-6.45, 2.3), (-6.55, 1.6), (-6.6, 0.0)]
CAP_TO = 5.0           # the point's dark cap (y above it)
NECK_SEAM = (-3.15, -2.85)   # a dark seam where the foot meets the neck
FOOT_END = -6.4        # the foot's dark end (y below it)
VISOR = (1.0, 2.15, 2.52)    # the visor: from y, to y, radius
SEGMENTS = 36


def materials():
    glow = k.level_palette()
    return {
        "grey": k.material("post_grey", palette=0x09, metallic=0.6, roughness=0.26),
        "dark": k.material("post_dark", palette=0x03, metallic=0.5, roughness=0.4),
        "visor": k.material("post_visor", palette=0x74, metallic=0.0, roughness=0.12, emission=glow[0x74],
                            emission_strength=1.4),
        "visor_hot": k.material("post_visor_hot", palette=0x76, metallic=0.0, roughness=0.1, emission=glow[0x76],
                                emission_strength=1.9),
    }


def body(m):
    """The post turned from its profile, about its axis along y; the cap, the seam and the foot's end dark."""
    post = k.lathe("post", list(reversed(PROFILE)), m["grey"], SEGMENTS, axis_z=AXIS_Z)  # in increasing y
    k.smooth(post, 50)

    def pick(c, n):
        if c.y > CAP_TO or NECK_SEAM[0] < c.y < NECK_SEAM[1] or c.y < FOOT_END:
            return m["dark"]
        return None
    mk.paint(post, pick)
    return post


def visor(m):
    """The visor: a ring of red glass in the head's groove, glowing, hottest along its top (a little left)."""
    y0, y1, r = VISOR
    profile = [(y0, r - 0.25), (y0 + 0.08, r - 0.02), (y0 + 0.22, r), (y1 - 0.22, r), (y1 - 0.08, r - 0.02),
               (y1, r - 0.25)]
    ring = k.lathe("visor", profile, m["visor"], SEGMENTS, axis_z=AXIS_Z)
    k.smooth(ring, 60)
    up = Vector((-0.35, 0.0, 1.0)).normalized()
    mk.paint(ring, lambda c, n: m["visor_hot"] if Vector((n.x, 0.0, n.z)).normalized().dot(up) > 0.8 else None)


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    m = materials()
    body(m)
    visor(m)
    parts = mk.meshes()
    bpy.context.view_layer.update()
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_5.png")
        mk.compare("visor_post (5 133)", mk.coverage(parts, 12, 14), k.sprite_mask(sheet, 133, large=False))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("visor_post", parts, os.path.join(out, "visor_post.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "visor_post", parts)  # framed like a 2x2 sprite, as the upscales are


if __name__ == "__main__":
    build()
