"""The tan fork ship of SAVARA and SAVARA Y (sheet F sprite 87, 2x2: 24 x 28 pixels; not animated; enemy 166: sky in
episodes 1 and 3, the ground layer in episode 5's SAVARA), polished (2026-10-19; it replaces wave2_g.py's
fork_ship(), parts inflated from the sprite's outline). models.cfg: sprite f 87 fork_ship yaw=0 (unchanged).

F 87 is F 3's pixels in other palette ramps, every pixel's shade the same (the green arrow of SAVARA, APPROACH and
INVADERS, polish_jets.py's jet_green): its green (ramp 2) drawn in tan (ramp 1), its khaki fins and elevons (ramp 1)
in grey (ramp 0), their orange highlights and the yellow intakes (ramp 7) in blue-grey (ramp 6). So the fork ship is
jet_green's model, not modelled again: this script builds it with polish_jets.build_green() and moves each palette
material to the fork ship's ramp (RAMPS), so the fins, elevons and intakes come out grey and blue-grey as the sprite
draws them. (models.cfg's color=sprite on jet_green would do without a model of its own, but it gives every palette
material the sprite's one main ramp: the fins, elevons and intakes would turn tan.)

Coordinates as polish_jets.py's: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera, origin at
the sprite's centre (pixel 12, 14); nose down the screen, as the sprite.

Replaces wave2_g.py's fork_ship() (its @model("fork_ship", "F", 87) function, the fork_ship line of the docstring)
and wave2_g_art.py's F87 (nothing else reads it): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_F.png), --preview <prefix> (top and 3/4 views).
"""
import os
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_jets as jets  # noqa: E402

SPRITE = 87
RAMPS = {2: 1, 1: 0, 7: 6}   # jet_green's ramp: the fork ship's (each shade kept)
ROLES = {"orange": "fin", "yellow": "intake"}   # jet_green's materials named after their colours, renamed
FIN = 0x6c                   # the fins and elevons a lighter blue-grey than their ramp's shade (the upscale's blades)
PORT_LIGHT = (0.0, -4.7, 0.6, 0.72, 0.3)     # the light in the port (the sprite's pixel 13, 18): u, y, radii


def recolour():
    """Each palette material "<name>@<index>" replaced by "fork_<role>@<the index in the fork ship's ramp>", its other
    settings kept."""
    made = {}
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        for slot, mat in enumerate(obj.data.materials):
            if mat is None or "@" not in mat.name:
                continue
            name, index = mat.name.rsplit("@", 1)
            index = int(index)
            new = (RAMPS.get(index >> 4, index >> 4) << 4) | (index & 15)
            role = name.split("_", 1)[1] if "_" in name else name
            role = ROLES.get(role, role)
            if role == "fin":
                new = FIN
            if mat.name not in made:
                bsdf = mat.node_tree.nodes["Principled BSDF"]
                made[mat.name] = k.material("fork_" + role, palette=new,
                                            metallic=bsdf.inputs["Metallic"].default_value,
                                            roughness=bsdf.inputs["Roughness"].default_value)
            obj.data.materials[slot] = made[mat.name]
    return made


def port_light():
    """The light in the port (jet_green's canopy, the fork ship's dark port): a small glowing lens on the glass."""
    glass = bpy.data.objects["canopy"]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(glass, depsgraph)
    u, y, rx, ry, rz = PORT_LIGHT
    x = u + jets.GREEN_AXIS
    hit, _, _, _ = tree.ray_cast(Vector((x, y, 50.0)), Vector((0, 0, -1)))
    z = hit.z if hit is not None else 3.0
    glow = k.level_palette()[0x1e]
    mat = k.material("fork_port_light", palette=0x1d, metallic=0.0, roughness=0.15, emission=glow,
                     emission_strength=0.7)
    k.smooth(k.ellipsoid("port_light", (x, y, z - rz * 0.45), (rx, ry, rz), mat, 16, 8), 60)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    jets.build_green()
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(Matrix.Translation((jets.GREEN_AXIS, 0, 0)))
    made = recolour()
    port_light()
    used = sorted({m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials})
    print("== fork_ship (F %d): %d triangles, %d materials: %s" % (SPRITE, jets.triangles(), len(used),
                                                                  ", ".join(used)))
    print("   ramps: " + ", ".join("%s -> %s" % (a, b.name) for a, b in sorted(made.items())))
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_F.png"), SPRITE)
    path = os.path.join(outdir, "fork_ship.glb")
    k.export(path)
    print("   fork_ship: %.1f KB" % (os.path.getsize(path) / 1024))
    if "preview" in options:
        jets.preview(options["preview"] + "fork_ship")


if __name__ == "__main__":
    build()
