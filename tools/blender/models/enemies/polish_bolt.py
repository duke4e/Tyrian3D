"""The steel bolt of APPROACH, BRAINIAC and DREAD-NOT (sheet 5 sprite 77, 2x2: a 13 x 27 bolt in the
24 x 28 cell; static; ground (BRAINIAC and APPROACH: enemy 524, set in the armoured claw gate 5 85 /
5 87 and then shot down the screen), sky and top (DREAD-NOT)), polished (2026-10-18; it replaces
later_episodes.py's bolt(), a plain lathe in two lumps with a red ring). models.cfg: sprite 5 77
bolt yaw=0.

As the 4x upscale draws it, a turned steel bolt lying along the screen, its point down: a two-tier
cap at the top (columns 6-18 of rows 0-4: a flange, a groove, a second flange and a cone narrowing
into the shaft), a ribbed shaft (columns 9-15: a bead at rows 5-6, a narrow neck at rows 7-8, two
beads at rows 9-12 with a shallow groove between them), a collar with a rounded shoulder (columns
7-17 of rows 14-16), a red band round it (rows 17-18) and a bullet-shaped head below (columns 6-18 of
rows 18-21, tapering to the point at row 26). The sprite lights every ring's upper face (the game's
sun comes from the top of the screen): the model's rings catch it the same way.

One lathe about the bolt's axis (x 0.5: the sprite is symmetric about its column 12), its
cross-section a little flattened towards the camera (SQUASH) so that it lies lower on the ground.
The steel takes the sprite's greys by where it is (the flanges and beads light, the grooves and the
neck dark); the red band glows a little in its own red.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <dir with enemy_5.png,
or the sheet itself> (the silhouette), --preview <prefix>.
"""
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402

AXIS_X = 0.5
SQUASH = 0.85
SEGMENTS = 36

# The profile from the point (row 26) up to the cap's top (row 0): (y, radius, part). y is the
# sprite's row edge (14 - row); the radii reach most of the way into the sprite's dark outline.
# Parts: "cone" (the head's lower half, darker as the sprite draws it), "head" (its shoulder), "band",
# "collar", "shaft", "dark" (grooves and the neck), "flange", "top".
PROFILE = [
    (-12.95, 0.0, "cone"),
    (-12.75, 0.75, "cone"), (-12.3, 1.45, "cone"), (-11.5, 2.35, "cone"), (-10.5, 3.35, "cone"),
    (-9.5, 4.3, "cone"), (-8.5, 5.15, "cone"), (-7.6, 5.75, "cone"), (-6.8, 6.1, "head"),
    (-6.1, 6.25, "head"), (-5.55, 6.2, "head"), (-5.2, 6.0, "head"), (-5.0, 5.65, "head"),
    (-4.92, 5.25, "band"),
    # The red band (rows 17-18), standing out a little between the head and the collar.
    (-4.85, 5.32, "band"), (-4.55, 5.42, "band"), (-3.45, 5.42, "band"), (-3.15, 5.32, "band"),
    (-3.08, 5.1, "collar"),
    # The collar (rows 14-16): straight, its top rounding over into the shaft.
    (-2.9, 5.22, "collar"), (-2.2, 5.3, "collar"), (-1.3, 5.3, "collar"), (-0.8, 5.15, "collar"),
    (-0.45, 4.8, "collar"), (-0.2, 4.2, "collar"), (-0.05, 3.5, "collar"),
    (0.05, 2.85, "dark"), (0.5, 2.7, "dark"),
    # The shaft: the lower bead (row 12), a shallow groove (row 11), the long bead (rows 9-10).
    (1.0, 2.95, "shaft"), (1.5, 3.15, "shaft"), (2.0, 3.0, "shaft"),
    (2.35, 2.78, "dark"), (2.65, 2.78, "dark"),
    (3.0, 3.0, "shaft"), (3.6, 3.2, "shaft"), (4.3, 3.15, "shaft"), (4.75, 2.85, "shaft"),
    # The neck (rows 7-8).
    (5.1, 2.35, "dark"), (5.5, 2.1, "dark"), (6.5, 2.1, "dark"), (6.9, 2.35, "dark"),
    # The upper bead (rows 5-6).
    (7.25, 2.85, "shaft"), (7.7, 3.2, "shaft"), (8.3, 3.2, "shaft"), (8.75, 2.95, "shaft"),
    # The cap: a cone out to the lower flange (row 4), the flange (row 3), the groove (row 2), the
    # top flange (row 1) and its chamfered top edge (row 0).
    (9.05, 3.25, "dark"), (9.4, 4.1, "flange"), (9.75, 5.0, "flange"), (10.05, 5.75, "flange"),
    (10.4, 6.1, "flange"), (10.9, 6.2, "flange"), (11.25, 6.0, "flange"),
    (11.45, 5.6, "dark"), (11.75, 5.55, "dark"),
    (11.95, 5.95, "flange"), (12.3, 6.2, "flange"), (13.0, 6.2, "flange"), (13.45, 5.95, "flange"),
    (13.75, 5.4, "top"), (13.92, 4.6, "top"), (13.98, 3.0, "top"),
]


def materials():
    red = k.level_palette()[0x75]
    # Steel half metallic: fully metallic it mirrors the game's dark surroundings and reads charcoal.
    return {
        "cone": k.material("bolt_cone", palette=0x08, metallic=0.45, roughness=0.24),
        "head": k.material("bolt_head", palette=0x0a, metallic=0.45, roughness=0.22),
        "collar": k.material("bolt_collar", palette=0x0b, metallic=0.45, roughness=0.2),
        "shaft": k.material("bolt_shaft", palette=0x0b, metallic=0.45, roughness=0.2),
        "flange": k.material("bolt_flange", palette=0x0c, metallic=0.45, roughness=0.18),
        "top": k.material("bolt_top", palette=0x08, metallic=0.45, roughness=0.25),
        "dark": k.material("bolt_groove", palette=0x05, metallic=0.45, roughness=0.3),
        "band": k.material("bolt_band", palette=0x75, metallic=0.2, roughness=0.3, emission=red,
                           emission_strength=0.45),
    }


def body(mats):
    """The bolt: rings along the profile (between the parts a ring on either side, so that the
    colours change along the ring edges), fans closing the point and the cap's top."""
    points = [(y, r) for y, r, _ in PROFILE]
    obj = k.lathe("bolt", points, None, segments=SEGMENTS, axis_x=AXIS_X, axis_z=0.0, squash=SQUASH)
    names = []
    for _, _, part in PROFILE:
        if mats[part].name not in names:
            names.append(mats[part].name)
            obj.data.materials.append(mats[part])
    # Faces between ring i and i + 1 take the part of the profile point above them (the rings are
    # the profile's points with r > 0; the first point is the point's fan).
    rings = [(y, r, part) for y, r, part in PROFILE if r > 0]
    for poly in obj.data.polygons:
        y = poly.center.y
        part = rings[-1][2]
        for (y0, _, _), (y1, _, upper) in zip(rings, rings[1:]):
            if y0 <= y <= y1:
                part = upper
                break
        if y < rings[0][0]:
            part = "cone"
        poly.material_index = names.index(mats[part].name)
    return k.smooth(obj, 38)


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            evaluated.to_mesh_clear()
    return total


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    body(materials())
    used = {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials}
    print("== bolt (5 77): %d triangles, %d materials" % (triangles(), len(used)))
    if "check" in options:
        sheet = options["check"]
        k.check_silhouette(os.path.join(sheet, "enemy_5.png") if os.path.isdir(sheet) else sheet, 77)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "bolt.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    if "preview" in options:
        k.preview(options["preview"] + "bolt")


if __name__ == "__main__":
    build()
