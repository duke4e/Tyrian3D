"""The red winged medallion of ASTCITY, AST ROCK and CORE (sheet D sprite 117 and sheet 3 sprite 52, the same pixels;
2x2: 24 x 23 pixels in the 24 x 28 cell; sky layer, enemies 826 and 1081, not animated), polished (2026-10-19; it
replaces wave3_j.py's medallion_red(), a plate inflated from the sprite's outline with tubes laid on for ridges).
models.cfg: sprite d 117 medallion_red yaw=0 glow=7:0.3:122:0:4 and sprite 3 52 medallion_red yaw=0
glow=7:0.3:122:0:4 (the gem's light, orange, where the ornament's line puts its blue one).

The medallion is the golden ornament (sheet D sprite 79, polish_ornament.py) pixel for pixel in other ramps: its gold
(ramp 1) is copper here (ramp 4, the same shades), its dark outline ramp 3's near-black instead of ramp 0's, and its
blue gem (ramp 3) an orange one (ramp 7, a shade or two apart in 10 of its 12 pixels). So it is built as
polish_ornament.py builds the brooch, with the same facets, ridges, bezel, scrolls and hanging loop, in copper; but
`color=sprite` on the ornament would not do, as the game would turn the gem copper too (palette materials all take
the sprite's main ramp) and its glow would stay blue. The gem is this model's own: a cut stone instead of the
ornament's cabochon, an octagonal table and eight crown facets round it over a girdle, glowing in the sprite's
shades: the table yellow (7d), the facets towards the light orange (7b), those away from it red-orange (78), the
girdle red (75), as the sprite draws it (7d at its upper left, 74-75 at its bottom).

polish_ornament.py's build() is run here with tyrkit's material() handing out the copper materials for the gold
ones and its finish() doing nothing; the gem it makes is replaced.

Origin at the sprite's centre (pixel 12, 14); +X right, +Y up the sprite, +Z towards the camera (the brooch's back
on z = 0; the game centres it in height on its layer).

Replaces wave3_j.py's medallion_red() (its @model("medallion_red", [(D, 117, True)]) registration; wave3_j_art.py's
D117 goes with it, nothing else uses it): remove it so that it doesn't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_D.png's 117), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402

# The ornament's materials (by name) and the copper ones that take their place: palette index (its shade in ramp 4,
# as the gold's in ramp 1), metallic, roughness.
COPPER = {
    "ornament_backing": ("medal_backing", 0x42, 0.25, 0.5),
    "ornament_gold": ("medal_copper", 0x49, 0.5, 0.3),
    "ornament_gold_mid": ("medal_copper_mid", 0x48, 0.5, 0.32),
    "ornament_gold_low": ("medal_copper_low", 0x46, 0.5, 0.34),
    "ornament_ridge": ("medal_ridge", 0x4d, 0.35, 0.24),
    "ornament_bezel": ("medal_bezel", 0x4b, 0.5, 0.24),
    "ornament_loop": ("medal_loop", 0x4a, 0.5, 0.26),
    "ornament_bead": ("medal_bead", 0x4b, 0.45, 0.27),
    "ornament_socket": ("medal_socket", 0x41, 0.1, 0.65),
    "ornament_gem": ("medal_cabochon", 0x75, 0.1, 0.1),   # replaced by the cut stone
}
# The gem: its girdle's radius and height (above the brooch's lift at the gem), the table's radius and height, the
# pavilion's depth into the bezel; the facets' colours: (palette index, emission strength).
GIRDLE_R, GIRDLE_Z, GIRDLE_H = 2.3, 2.55, 0.35
TABLE_R, TABLE_Z = 1.15, 4.15
PAVILION_Z = 1.7
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()     # the game's sun, from the upper left
GEM = {"table": (0x7d, 1.7), "lit": (0x7b, 1.3), "shade": (0x78, 0.95), "girdle": (0x75, 0.7)}


def ornament():
    """polish_ornament.py's definitions (it builds the brooch only when run as a script)."""
    sys.path.insert(0, HERE)
    import polish_ornament
    return polish_ornament


class CopperKit:
    """tyrkit for polish_ornament's build(): its gold materials handed out as copper ones, nothing exported."""

    def __init__(self):
        self.made = {}

    def __getattr__(self, name):
        return getattr(k, name)

    def material(self, name, **_):
        if name not in self.made:
            new, index, metallic, roughness = COPPER[name]
            self.made[name] = k.material(new, palette=index, metallic=metallic, roughness=roughness)
        return self.made[name]

    def finish(self, *_, **__):
        pass


def gem_materials():
    glow = k.level_palette()
    return {key: k.material(f"medal_gem_{key}", palette=index, metallic=0.1, roughness=0.08, emission=glow[index],
                            emission_strength=strength) for key, (index, strength) in GEM.items()}


def cut_gem(centre, lift, mats):
    """An octagonal cut stone: the table, eight crown facets down to the girdle (each coloured by how it faces the
    light), the girdle, the pavilion down into the bezel. Flat shaded, as a cut stone is."""
    cx, cy = centre
    n = 8
    turn = math.pi / 8    # a facet, not a corner, faces straight up the screen

    def ring(radius, z, offset=0.0):
        return [Vector((cx + radius * math.cos(turn + offset + 2 * math.pi * i / n),
                        cy + radius * math.sin(turn + offset + 2 * math.pi * i / n), lift + z)) for i in range(n)]
    table = ring(TABLE_R, TABLE_Z)
    crown = ring(GIRDLE_R, GIRDLE_Z + GIRDLE_H)
    girdle = ring(GIRDLE_R, GIRDLE_Z)
    vertices = table + crown + girdle + [Vector((cx, cy, lift + PAVILION_Z))]
    tip = len(vertices) - 1
    faces, kinds = [], []
    faces.append(tuple(range(n)))
    kinds.append("table")
    for i in range(n):
        j = (i + 1) % n
        quad = (i, n + i, n + j, j)
        normal = (crown[i] - table[i]).cross(table[j] - table[i]).normalized()
        if normal.z < 0:
            normal = -normal
        faces.append(quad)
        kinds.append("lit" if normal.dot(LIGHT) > 0.8 else "shade")
        faces.append((n + i, 2 * n + i, 2 * n + j, n + j))
        kinds.append("girdle")
        faces.append((2 * n + i, tip, 2 * n + j))
        kinds.append("girdle")
    obj = k.mesh_object("gem_cut", [tuple(v) for v in vertices], faces)
    names = []
    for kind in kinds:
        if mats[kind].name not in names:
            names.append(mats[kind].name)
            obj.data.materials.append(mats[kind])
    for poly, kind in zip(obj.data.polygons, kinds):
        poly.material_index = names.index(mats[kind].name)
    k.recalc_normals(obj)
    for poly in obj.data.polygons:
        poly.use_smooth = False
    return obj


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    orn = ornament()
    orn.k = CopperKit()
    orn.build()
    # The ornament's cabochon gives way to the cut stone.
    old = bpy.data.objects["gem"]
    bpy.data.objects.remove(old)
    cut_gem(orn.GEM, orn.convex(*orn.GEM), gem_materials())
    parts = mk.meshes()
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    if "check" in options:
        mk.compare("medallion_red (D 117, 3 52)", mk.coverage(parts, 24, 28),
                   k.sprite_mask(os.path.join(options["check"], "enemy_D.png"), 117))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("medallion_red", parts, os.path.join(out, "medallion_red.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "medallion_red", parts)


if __name__ == "__main__":
    build()
