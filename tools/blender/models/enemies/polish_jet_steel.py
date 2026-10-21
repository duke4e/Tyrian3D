"""The blue-grey jet of SAVARA, SAVARA Y and INVADERS (sheet F sprite 79, 2x2: 24 x 28 pixels; not animated; enemy 169,
sky layer: 8 in episode 1's SAVARA, 6 in SAVARA Y, 4 in episode 5's SAVARA, 6 in INVADERS), polished (2026-10-21; it
replaces wave2_f.py's jet_steel(), a lathed fuselage with slab wings and glowing navigation lights). models.cfg:
sprite f 79 jet_steel yaw=0 (unchanged); a sky enemy, which the game centres in height.

F 79 is F 125's pixels in another palette ramp: the same silhouette pixel for pixel, and every pixel's shade raised by
three in the blue-grey ramp (ramp 6) where F 125 draws it in grey (ramp 0), index s -> 0x60 + s + 3 (the dark outline,
shade 1, -> 0x60, the ramp's darkest; --check counts the pixels that don't follow this). Not mirrored, not turned
(mirrored, the shades no longer match). F 125 is the grey early jet with straight tapered wings, side intakes in
front of the wing roots, a bubble canopy and a cruciform tail, polished in polish_jets.py (jet_cross). So the steel
jet is jet_cross's model, not modelled again (as polish_fork_ship.py builds F 87, F 3's pixels in other ramps, from
jet_green): this script builds it with polish_jets.build_cross() and moves each of its palette materials to the
steel jet's index, its shade raised by three in ramp 6 (SHADE_UP; metallic and roughness kept): the hull 0x6b, the
wings 0x6a, the ailerons 0x6c, the canopy's frame 0x68, the nozzle 0x67, the seams and the glass 0x66, the intakes'
dark 0x64. (models.cfg's color=sprite on jet_cross would do without a model of its own, but it keeps each
material's shade: the jet would come out three shades darker than the sprite.) No emission: jet_cross has none
(the old model's glowing red and green wing-tip lights and exhaust are not in the sprite).

Coordinates as polish_jets.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera, origin at
the sprite's centre (pixel 12, 14); nose down the screen, as the sprite; the jet's axis on the sprite's column 12
(x 0.5).

Replaces wave2_f.py's jet_steel() (its @model("jet_steel", "enemy_F", 79) function and the jet_steel line of the
module's docstring): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_F.png, and the recolour check of F 79 against F 125), --preview <prefix> (top and 3/4 views).
"""
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_jets as jets  # noqa: E402
import polish_machine_kit as mk  # noqa: E402

SPRITE, SOURCE = 79, 125   # the steel jet's sprite, and jet_cross's whose pixels it is
RAMP, SHADE_UP = 6, 3      # jet_cross's ramp-0 shades move to ramp 6, three shades lighter
AXIS = 0.5                 # jet_cross's axis (polish_jets.JETS)


def steel_index(index):
    return (RAMP << 4) | min(15, (index & 15) + SHADE_UP)


def recolour():
    """Each palette material "jetcross_<role>@<index>" replaced by "jetsteel_<role>@<the steel jet's index>", its
    other settings kept. Returns {old name: new material}."""
    made = {}
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        for slot, mat in enumerate(obj.data.materials):
            if mat is None or "@" not in mat.name:
                continue
            name, index = mat.name.rsplit("@", 1)
            role = name.split("_", 1)[1] if "_" in name else name
            if mat.name not in made:
                bsdf = mat.node_tree.nodes["Principled BSDF"]
                made[mat.name] = k.material("jetsteel_" + role, palette=steel_index(int(index)),
                                            metallic=bsdf.inputs["Metallic"].default_value,
                                            roughness=bsdf.inputs["Roughness"].default_value)
            obj.data.materials[slot] = made[mat.name]
    return made


def recolour_check(sheet):
    """How many of F 79's pixels are not F 125's recoloured (s -> 0x60 + s + 3; the outline, 1 -> 0x60)."""
    from sprite_profile import sprite_indices
    a, b = sprite_indices(sheet, SOURCE), sprite_indices(sheet, SPRITE)
    differ = 0
    for r in range(28):
        for c in range(24):
            p, q = a[r][c], b[r][c]
            if (p is None) != (q is None):
                differ += 1
            elif p is not None and q != steel_index(p) and not (p == 0x01 and q == 0x60):
                differ += 1
    print("recolour check: %d pixels of F %d are not F %d's recoloured" % (differ, SPRITE, SOURCE))


def triangulate():
    """Every face split into triangles (the same split every run), so that the export doesn't split them itself."""
    for obj in mk.meshes():
        mod = obj.modifiers.new("triangulate", "TRIANGULATE")
        mod.quad_method = "BEAUTY"
        mod.ngon_method = "BEAUTY"
        mod.min_vertices = 4
        mod.keep_custom_normals = True
        mk.apply(obj)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    jets.build_cross()
    for obj in mk.meshes():
        obj.data.transform(Matrix.Translation((AXIS, 0, 0)))
    made = recolour()
    triangulate()
    used = sorted({m.name for o in mk.meshes() for m in o.data.materials})
    print("== jet_steel (F %d): %d triangles, %d materials: %s" % (SPRITE, jets.triangles(), len(used),
                                                                   ", ".join(used)))
    print("   ramps: " + ", ".join("%s -> %s" % (a, b.name) for a, b in sorted(made.items())))
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_F.png")
        recolour_check(sheet)
        k.check_silhouette(sheet, SPRITE)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "jet_steel.glb")
    k.export(path)
    print("   jet_steel: %.1f KB" % (os.path.getsize(path) / 1024))
    if "preview" in options:
        jets.preview(options["preview"] + "jet_steel")


if __name__ == "__main__":
    build()
